#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import json

from bson import json_util
from dateutil.relativedelta import relativedelta
from flask import request
from flask_restful import Resource
from flask_security import auth_token_required
from os.path import dirname
from lingobarter.core.json import render_json
from lingobarter.core.json import render_response
from lingobarter.utils import get_current_user
from ..accounts.models import User

# in database: teach_langs is what I want to teach , and learn_langs is what I want to learn


# response: list of results of /users/<userid> get
# 20 users per page (skip, limit)
class SearchResource(Resource):
    """
    Search the database using filter conditions passes in
    Return a list of user profiles that meet all search conditions
    We will return results page by page, 20 records per page

        # 'age_range': list of two elements, representing smallest and largest age acceptable
        # 'nationaliry': list of strings, representing names of countries acceptable
        # 'teach_langs': list of language items, language_id representing acceptable teach languages of other users
        # 'learn_langs': list of language items (language_id represents acceptable learn languages of other users,
        #                                        level represents acceptable learn languages of other users
        #                                        default value of level is 0)
        # 'has_bio': bool, if true, only accept users who have bio in their profile
        # 'area': dictionary.
        #        type: type of area, we currently only support Polygon
        #        coordinates: a list of [float(x), float(y)]
        #        we currently only search for users whose location's type is point
        # 'sort_by_nearest': bool, if true, sort by distance to current user's location
        #                    default: false
    """

    @auth_token_required
    def post(self):
        # get current user
        user = get_current_user()

        # we save all filter conditions and corresponding values here
        # 'age_range': list of two int, representing smallest and largest age acceptable
        # 'nationality': list of strings, representing numbers of countries acceptable
        # 'teach_langs': list of LanguageItems, representing acceptable teach languages of other users
        #                level will be ignored
        # 'learn_langs': list of LanguageItems, representing acceptable learn languages of other users
        #                level will not be ignored, set to be 0 if not provided
        # 'has_bio': a bool value, if true, only accept users who have bio in their profile
        #            this value will not be False
        # 'area': dictionary.
        #        type: type of area, we currently only support Polygon
        #        coordinates: a list of [float(x), float(y)]
        #        we currently only search for users whose location's type is point
        # 'sort_by_nearest': bool, if true, sort by distance to current user's location
        #                    default: false
        filter_conditions = {}

        # we get filter data from front end
        filter_data = json.loads(request.data, object_hook=json_util.object_hook)

        # parse filter data
        if filter_data.get('age_range') is not None:
            filter_conditions['age_range'] = [int(x) for x in filter_data['age_range']]
        if filter_data.get('nationality') is not None:
            filter_conditions['nationality'] = filter_data['nationality']
        if filter_data.get('teach_langs') is not None:
            filter_conditions['teach_langs_id_list'] = []
            for language in filter_data['teach_langs']:
                filter_conditions['teach_langs_id_list'].append(language['language_id'])

        if filter_data.get('learn_langs') is not None:
            filter_conditions['learn_langs_id_list'] = []
            filter_conditions['learn_langs_level_list'] = []
            for language in filter_data['learn_langs']:
                filter_conditions['learn_langs_id_list'].append(language['language_id'])
                if language.get('level') is not None:
                    filter_conditions['learn_langs_level_list'].append([int(level) for level in language['level']])
                else:
                    filter_conditions['learn_langs_level_list'].append([0, 5])  # set to default value

        if filter_data.get('has_bio') is not None:
            if bool(filter_data['has_bio']):  # if True, update filter condition
                filter_conditions['has_bio'] = True

        filter_conditions['page_id'] = filter_data['page_id'] if filter_data.get('page_id') is not None else 0

        filter_conditions['page_size'] = filter_data['page_size'] if filter_data.get('page_size') is not None else 20

        if filter_data.get('area') is not None:
            if filter_data['area'].get('type') == 'Polygon':
                if len(filter_data['area'].get('coordinates')) >= 3:
                    filter_conditions['area'] = {}
                    filter_conditions['area']['type'] = filter_data['area'].get('type')
                    filter_conditions['area']['coordinates'] = \
                        [[float(x), float(y)] for [x, y] in filter_data['area']['coordinates']]

        if filter_data.get('sort_by_nearest') is not None:
            if filter_data['sort_by_nearest']:
                filter_conditions['sort_by_nearest'] = True

        # generate query filter
        # age_range
        query_filter = []

        # here we consider settings of other users:
        # if other user's hide_from_search is set to be true, then nobody can find him
        query_filter.append({'settings.hide_from_search': {'$eq': False}})

        # here we consider settings of other usres:
        # can only be found by user within age range
        now_date = datetime.datetime.now().date()  # current date
        age = relativedelta(now_date, user.birthday).years
        query_filter.append({'$and':
                                 [{'settings.age_range.0': {'$lte': age}},
                                  {'settings.age_range.1': {'$gte': age}}]
                             })

        # here we consider settings of other users:
        # can only be found by users with same gender
        query_filter.append({'$or': [
            {'settings.same_gender': {'$eq': False}},
            {'$and': [
                {'settings.same_gender': {'$eq': True}},
                {'gender': {'$eq': user.gender}}]
            }]
        })

        if filter_conditions.get('age_range') is not None:
            least_birthday = datetime.datetime.now() - relativedelta(years=filter_conditions['age_range'][1])
            most_birthday = datetime.datetime.now() - relativedelta(years=filter_conditions['age_range'][0])
            query_filter.append({'birthday': {'$gte': least_birthday}})
            query_filter.append({'birthday': {'$lte': most_birthday}})

        # nationality
        if filter_conditions.get('nationality') is not None:
            query_filter.append({'nationality': {'$in': filter_conditions['nationality']}})

        # teach_langs
        if filter_conditions.get('teach_langs_id_list') is not None:
            teach_langs_query_filter = {'teach_langs.language_id': {'$in': filter_conditions['teach_langs_id_list']}}

        # learn_langs
        if filter_conditions.get('learn_langs_id_list') is not None:
            learn_langs_query_filter_list = []
            for i in range(len(filter_conditions['learn_langs_id_list'])):
                learn_langs_query_filter_list.append(
                    {'learn_langs': {
                        '$elemMatch': {
                            'language_id': {'$eq': filter_conditions['learn_langs_id_list'][i]},
                            '$and': [
                                {'level': {'$gte': filter_conditions['learn_langs_level_list'][i][0]}},
                                {'level': {'$lte': filter_conditions['learn_langs_level_list'][i][1]}}
                            ]
                        }
                    }
                    }
                )

            learn_language_query_filter = {'$or': learn_langs_query_filter_list}

            language_query_filter = {'$and': [teach_langs_query_filter, learn_language_query_filter]}
            query_filter.append(language_query_filter)

            # here we consider settings of other users:
            # when strict_lang_match is set to be true,
            # can only be found by user whose teach_langs and learn_langs match other user's learn_langs and teach_langs
            current_user_teach_langs = [language.language_id for language in user.teach_langs]
            current_user_learn_langs = [language.language_id for language in user.learn_langs]

            strict_teach_lang_query_filter = {'learn_langs.language_id': {'$in': current_user_teach_langs}}
            strict_learn_lang_query_filter = {'teach_langs.language_id': {'$in': current_user_learn_langs}}
            strict_lang_query_filter = {'$and': [strict_teach_lang_query_filter, strict_learn_lang_query_filter]}
            query_filter.append({
                '$or': [
                    {'settings.strict_lang_match': {'$eq': False}},
                    {'$and': [
                        {'settings.strict_lang_match': {'$eq': True}},
                        strict_lang_query_filter]
                    }
                ]
            })

        # has_bio
        if filter_conditions.get('has_bio') is not None:
            query_filter.append({'bio': {'$exists': True}})

        # area
        # we currently only search for users whose location's type is point
        if filter_conditions.get('area') is not None:
            if filter_conditions['area'].get('type') == 'Polygon':
                query_filter.append(
                    {
                        '$and': [
                            {'location.type': {'$eq': 'Point'}},
                            {'location.coordinates': {
                                '$geoWithin': {
                                    '$polygon': filter_conditions['area']['coordinates'] }
                                }
                            }
                        ]
                    }
                )

        # sort by nearest
        # We currently only support this functionality when user's location is Point
        if (filter_conditions.get('sort_by_nearest') is not None) and (filter_conditions['sort_by_nearest']):
            if (user.location['type'] == 'Point') and (len(user.location['coordinates']) == 2):
                query_filter.append(
                    {'$and': [
                        {'location.type': {'$eq': 'Point'}},
                        {'location.coordinates': {'$size': 2}},
                        {'location.coordinates': {'$nearSphere': user.location.coordinates}}
                    ]}
                )

        # we also need to filter out the user himself
        query_filter.append({'username': {'$ne': user.username}})

        # combine all query condition filters
        query = {'$and': query_filter}

        # query
        start_record_num = filter_conditions['page_id'] * filter_conditions['page_size']
        end_record_num = start_record_num + filter_conditions['page_size']
        acceptable_users = User.objects(__raw__=query)[start_record_num: end_record_num]

        # get acceptable users' profiles
        acceptable_users_profiles = []
        for acceptable_user in acceptable_users:
            acceptable_users_profiles.append(User.get_other_profile(acceptable_user.username))
        return render_response(acceptable_users_profiles)


class ContentResource(Resource):
    @auth_token_required
    def post(self):
        user = get_current_user()

        data = json.loads(request.data, object_hook=json_util.object_hook)
        if data.get('content') is None:
            return render_json(message='Please give me content', status=400)
        else:
            # append to file
            print data['content']
            print type(str(data['content']))
            print str(data['content'])
            with open(dirname(__file__) + "/../../mediafiles/" + user.username + "_chat_contents.txt", 'a') as chat_log:
                chat_log.write(str(data['content']) + " ")

            return render_json(message='Successfully get content', status=200)

