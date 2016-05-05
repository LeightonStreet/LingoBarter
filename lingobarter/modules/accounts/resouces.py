#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request
from flask_restful import Resource, reqparse, fields
from flask_security import utils, auth_token_required
from flask.ext.security.registerable import register_user
from lingobarter.core.json import render_json
from lingobarter.utils import get_current_user, dateformat
from .models import User
from bson import json_util
import json
import datetime
import pytz
from lingobarter.modules.accounts.models import Location, LanguageItem
from lingobarter.core.db import db

"""
Parsers
=======
one can extend from another
"""
# LoginResource:post
loginParser = reqparse.RequestParser()
loginParser.add_argument('email', type=str, required=True)
loginParser.add_argument('password', type=str, required=True)

signupParser = reqparse.RequestParser()
signupParser.add_argument('email', type=str, required=True)
signupParser.add_argument('username', type=str, required=True)
signupParser.add_argument('password', type=str, required=True)

updateProfileParse = reqparse.RequestParser()
updateProfileParse.add_argument('name', type=str, help='invalid name')
updateProfileParse.add_argument('tagline', type=str, help='invalid tagline')
updateProfileParse.add_argument('bio', type=str, help='invalid bio')
updateProfileParse.add_argument('teach_langs', type=list, help='invalid teach_langs') # todo
updateProfileParse.add_argument('learn_langs', type=list, help='invalid learn_langs') # todo
updateProfileParse.add_argument('location', type=dict, help='invalid location') #todo
updateProfileParse.add_argument('birthday', type=fields.datetime, help='invalid birthday') #todo
updateProfileParse.add_argument('gender', type=str, help='invalid gender')
updateProfileParse.add_argument('nationality', type=str, help='invalid nationality')

class LoginResource(Resource):
    def post(self):
        # parse arguments
        args = loginParser.parse_args()
        # get user
        user = User.get_user(email=args['email'])
        if not user:
            return render_json(message={'email': 'User does not exist'}, status=404)
        else:
            if not utils.verify_and_update_password(args['password'], user):
                return render_json(message={'password': 'Invalid password'}, status=406)
            else:
                if not user.confirmed_at:
                    return render_json(message={'email': 'Please confirm your email address'}, status=403)
                utils.login_user(user)
                token = user.get_auth_token()
                return render_json(message='Successfully log in', status=200,
                                   auth_token=token, user_id=str(user.id),
                                   username=user.username, name=user.name,
                                   complete=user.complete)


class LogoutResource(Resource):
    """
    Log out
    """
    @auth_token_required
    def get(self):
        utils.logout_user()
        return render_json(message='Successfully log out', status=200)


class UserResource(Resource):
    """
    Sign up
    """
    def post(self):
        # parse arguments
        args = signupParser.parse_args()
        unique_flag = False
        message = {}
        if User.get_user(args['email']):
            unique_flag = True
            message['email'] = 'Email address has been taken'
        if User.get_user_by_username(args['username']):
            unique_flag = True
            message['username'] = 'Username has been taken'
        if unique_flag:
            return render_json(message=message, status=409)

        user = register_user(**args)
        return render_json(message='User has been created. You need to confirm the email to log in', status=200,
                           email=user.email)

    """
    User view him/her own profile
    """
    @auth_token_required
    def get(self):
        user = get_current_user()
        teach_languages = []
        learn_languages = []

        for tech_language in user.teach_langs:
            teach_languages.append({
                'language_id': tech_language.language_id,
                'level': tech_language.level
            })

        for learn_language in user.learn_langs:
            learn_languages.append({
                'language_id': learn_language.language_id,
                'level': learn_language.level
            })

        return render_json(
            message='Successfully get user own profile',
            status=200,
            response={
                'name': user.username if user.name is None else user.name,
                'email': user.email,
                'username': user.username,
                'tagline': user.tagline,
                'bio': user.bio,
                'avatar_url': user.get_avatar_url() if user.avatar_file_path is not None else None,
                'teach_langs': teach_languages,
                'learn_langs': learn_languages,
                'location': None if user.location is None
                    else {'type': user.location.type, 'coordinates': user.location.coordinates},
                'birthday': dateformat.datetime_to_timestamp(user.birthday),
                'gender': user.gender,
                'settings': user.settings.to_mongo(),
                'learn_points': user.learn_points.to_mongo(),
                'nationality': user.nationality
            }
        )

    """
    User configure & update himself/ herself's profile
    Note: User can never update email or username
    """
    @auth_token_required
    def put(self):
        # get current user
        user = get_current_user()

        # get new profile
        new_profile = json.loads(json.loads(request.data, object_hook=json_util.object_hook)['data'])

        # parse new profile
        user.name = new_profile['name']                 # update name
        user.tagline = new_profile['tagline']           # update tagline
        user.bio = new_profile['bio']                   # update bio

        # update teach_langs
        new_teach_langs = new_profile['teach_langs']
        new_teach_languageitem_list = []
        for language in new_teach_langs:
            new_language_item = LanguageItem()
            new_language_item.language_id = language['language_id']
            new_language_item.level = int(language['level'])
            new_teach_languageitem_list.append(new_language_item)
        user.teach_langs = new_teach_languageitem_list

        # update learn_langs
        new_learn_langs = new_profile['learn_langs']
        new_learn_languageitem_list = []
        for language in new_learn_langs:
            new_language_item = LanguageItem()
            new_language_item.language_id = language['language_id']
            new_language_item.level = int(language['level'])
            new_learn_languageitem_list.append(new_language_item)
        user.learn_langs = new_learn_languageitem_list

        # update location
        if user.location is None:
            user.location = Location()
        user.location.type = new_profile['location']['type']
        user.location.coordinates = [db.FloatField(x) for x in new_profile['location']['coordinates']]

        # update birthday
        new_ts = new_profile['birthday']['$date']
        user.birthday = datetime.datetime.fromtimestamp(new_ts/1000, pytz.timezone('GMT'))

        user.gender = new_profile['gender']             # update gender
        user.nationality = new_profile['nationality']   # update nationality

        if user.save():
            return render_json(message='Successfully updated user profile', status=200)
        else:
            return render_json(message='Fail to update user profile', status=400)




    """
    User delete his/her own account
    """
    @auth_token_required
    def delete(self):
        pass


class UserViewResource(Resource):
    """
    User profile view
    """

    """
    User view other user's profile
    """
    @auth_token_required
    def get(self, username):
        user = User.get_user_by_username(username)

        if user is None:
            return render_json(
                message={'username': username + ' does not exist'},
                status=404
            )

        teach_languages = []
        learn_languages = []

        for tech_language in user.teach_langs:
            teach_languages.append({
                'language_id': tech_language.language_id,
                'level': tech_language.level
            })

        for learn_language in user.learn_langs:
            learn_languages.append({
                'language_id': learn_language.language_id,
                'level': learn_language.level
            })

        # could be ['location', 'nationality', 'birthday', 'current_login_at', 'gender']
        invisible_fields = user.settings.hide_info_fields

        print type(user.current_login_at)

        return render_json(
            message='View ' + username + "'s profile",
            status=200,
            response={
                'name': user.username if user.name is None else user.name,
                'username': user.username,
                'tagline': user.tagline,
                'bio': user.bio,
                'avatar_url': user.get_avatar_url() if user.avatar_file_path is not None else None,
                'teach_langs': teach_languages,
                'learn_langs': learn_languages,
                'location': {'type': user.location.type, 'coordinates': user.location.coordinates}
                    if user.location and 'location' not in invisible_fields else None,
                'birthday': dateformat.datetime_to_timestamp(user.birthday)
                    if 'birthday' not in invisible_fields else None,
                'gender': user.gender if 'gender' not in invisible_fields else None,
                'nationality': user.nationality if 'nationality' not in invisible_fields else None,
                'current_login_at': dateformat.datetime_to_timestamp(user.current_login_at)
                    if 'current_login_at' not in invisible_fields else None
            }
        )
