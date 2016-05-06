#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from bson import json_util

from flask_restful import Resource
from flask_security import auth_token_required
from flask import request

# from mongoengine.queryset.visitor import Q

from lingobarter.utils import get_current_user
from lingobarter.core.json import render_json
from ..accounts.models import User, LanguageItem

import datetime
from dateutil.relativedelta import relativedelta


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
        filter_conditions = {}

        # we get filter data from front end
        filter_data = json.loads(request.data, object_hook=json_util.object_hook)

        # parse filter data
        if filter_data.get('age_range') is not None:
            filter_conditions['age_range'] = [int(x) for x in filter_data['age_range']]
        if filter_data.get('nationality') is not None:
            filter_conditions['nationality'] = filter_data['nationality']
        if filter_data.get('teach_langs') is not None:
            filter_conditions['teach_langs'] = []
            for language in filter_data['teach_langs']:
                new_language_item = LanguageItem()
                new_language_item.language_id = language['language_id']
                filter_conditions['teach_langs'].append(new_language_item)
        if filter_data.get('learn_langs') is not None:
            filter_conditions['learn_langs'] = []
            for language in filter_data['learn_langs']:
                new_language_item = LanguageItem()
                new_language_item.language_id = language['language_id']
                new_language_item.level = int(language['level']) if language.get('level') is not None else 0
                filter_conditions['learn_langs'].append(new_language_item)
        if filter_data.get('has_bio') is not None:
            if bool(filter_data['has_bio']): # if True, update filter condition
                filter_conditions['has_bio'] = True

        # generate query filter
        # age_range
        query_filter = []
        if filter_conditions.get('age_range') is not None:
            least_birthday = datetime.datetime.now() - relativedelta(years=filter_conditions['age_range'][1])
            most_birthday = datetime.datetime.now() - relativedelta(years=filter_conditions['age_range'][0])
            query_filter.append({'birthday': {'$gte': least_birthday}})
            query_filter.append({'birthday': {'$lte': most_birthday}})

        # nationality
        if filter_conditions.get('nationality') is not None:
            query_filter.append({'nationality': {'$in': filter_conditions['nationality']}})

        # teach_langs
        if filter_conditions.get('teach_langs') is not None:
            teach_language_id_list = [language.language_id for language in filter_conditions['teach_langs']]
            query_filter.append({'teach_langs.language_id': {'$in': teach_language_id_list}})

        # learn_langs
        if filter_conditions.get('learn_langs') is not None:
            learn_langs_query_filter = []
            for language in filter_conditions['learn_langs']:
                learn_langs_query_filter.append(
                    {'learn_langs':{
                        '$elemMatch': {
                            'language_id': {'$eq': language.language_id},
                            'level': {'$gte': language.level}
                        }
                    }
                    }
                )
            query_filter.append({'$or': learn_langs_query_filter})

        # has_bio
        if filter_conditions.get('has_bio') is not None:
            query_filter.append({'bio': {'$exists': True}})

        # we also need to filter out the user himself
        query_filter.append({'username': {'$ne': user.username}})

        # combine all query condition filters
        query = {'$and': query_filter}

        # query
        acceptable_users = User.objects(__raw__=query)

        # print result
        print "*********************"
        for x in acceptable_users:
            print x.email

        return render_json(message='Successfully search users.', status=200)













