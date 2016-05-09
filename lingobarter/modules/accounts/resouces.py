#!/usr/bin/env python
# -*- coding: utf-8 -*-

import errno
import json

import os
from bson import json_util
from flask import request, current_app
from flask.ext.security.confirmable import send_confirmation_instructions
from flask.ext.security.recoverable import send_reset_password_instructions
from flask.ext.security.registerable import register_user
from flask_restful import Resource, reqparse, fields
from flask_security import utils, auth_token_required
from lingobarter.core.json import render_json
from lingobarter.utils import get_current_user, dateformat
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from .models import User, Location, LanguageItem

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
updateProfileParse.add_argument('teach_langs', type=list, help='invalid teach_langs')  # todo
updateProfileParse.add_argument('learn_langs', type=list, help='invalid learn_langs')  # todo
updateProfileParse.add_argument('location', type=dict, help='invalid location')  # todo
updateProfileParse.add_argument('birthday', type=fields.datetime, help='invalid birthday')  # todo
updateProfileParse.add_argument('gender', type=str, help='invalid gender')
updateProfileParse.add_argument('nationality', type=str, help='invalid nationality')

uploadAvatarParse = reqparse.RequestParser()
uploadAvatarParse.add_argument('image', required=True, type=FileStorage, location='files')


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

    @auth_token_required
    def get(self):
        """
        User view him/her own profile
        """
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
                'id': str(user.id),
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

    @auth_token_required
    def put(self):
        """
        User configure & update himself/ herself's profile
        Note: User can never update email or username
        """

        # get current user
        user = get_current_user()

        # get new profile
        new_profile = json.loads(request.data, object_hook=json_util.object_hook)

        # parse new profile
        user.name = new_profile['name'] if new_profile.get('name') is not None else user.name  # update name
        user.tagline = new_profile['tagline'] if new_profile.get(
            'tagline') is not None else user.tagline  # update tagline
        user.bio = new_profile['bio'] if new_profile.get('bio') is not None else user.bio  # update bio

        # update teach_langs
        new_teach_langs = new_profile.get('teach_langs')
        if new_teach_langs is not None:
            new_teach_languageitem_list = []
            for language in new_teach_langs:
                new_language_item = LanguageItem()
                new_language_item.language_id = language['language_id']
                new_language_item.level = int(language['level'])
                new_teach_languageitem_list.append(new_language_item)
            user.teach_langs = new_teach_languageitem_list

        # update learn_langs
        new_learn_langs = new_profile.get('learn_langs')
        if new_learn_langs is not None:
            new_learn_languageitem_list = []
            for language in new_learn_langs:
                new_language_item = LanguageItem()
                new_language_item.language_id = language['language_id']
                new_language_item.level = int(language['level'])
                new_learn_languageitem_list.append(new_language_item)
            user.learn_langs = new_learn_languageitem_list

        # update location
        if new_profile.get('location') is not None:
            if user.location is None:
                user.location = Location()
            user.location.type = new_profile['location']['type']
            user.location.coordinates = [float(x) for x in new_profile['location']['coordinates']]

        # update birthday
        if new_profile.get('birthday') is not None:
            user.birthday = dateformat.timestamp_to_datetime(new_profile['birthday'])
        # update gender
        user.gender = new_profile['gender'] if new_profile.get('gender') is not None else user.gender
        # update nationality
        user.nationality = new_profile['nationality'] if new_profile.get(
            'nationality') is not None else user.nationality

        # update settings
        if new_profile.get('settings') is not None:
            new_settings = new_profile['settings']

            user.settings.strict_lang_match = bool(new_settings['strict_lang_match']) \
                if new_settings.get('strict_lang_match') is not None else user.settings.strict_lang_match
            user.settings.same_gender = bool(new_settings['same_gender']) \
                if new_settings.get('same_gender') is not None else user.settings.same_gender
            user.settings.age_range = [int(x) for x in new_settings['age_range']] \
                if new_settings.get('age_range') is not None else user.settings.age_range
            user.settings.hide_from_nearby = bool(new_settings['hide_from_nearby']) \
                if new_settings.get('hide_from_nearby') is not None else user.settings.hide_from_nearby
            user.settings.hide_from_search = bool(new_settings['hide_from_search']) \
                if new_settings.get('hide_from_search') is not None else user.settings.hide_from_search
            user.settings.hide_info_fields = new_settings['hide_info_fields'] if new_settings.get('hide_info_fields') \
                                                                                 is not None else user.settings.hide_info_fields
            user.settings.partner_confirmation = bool(new_settings['partner_confirmation']) \
                if new_settings.get('partner_confirmation') is not None else user.settings.partner_confirmation

        # update learn_points
        if new_profile.get('learn_points') is not None:
            new_learn_points = new_profile['learn_points']

            user.learn_points.favorites = int(new_learn_points['favorites']) \
                if new_learn_points.get('favorites') is not None else user.learn_points.favorites
            user.learn_points.pronunciations = int(new_learn_points['pronunciations']) \
                if new_learn_points.get('pronunciations') is not None else user.learn_points.pronunciations
            user.learn_points.translations = int(new_learn_points['translations']) \
                if new_learn_points.get('translations') is not None else user.learn_points.translations
            user.learn_points.transliterations = int(new_learn_points['transliterations']) \
                if new_learn_points.get('transliterations') is not None else user.learn_points.transliterations
            user.learn_points.corrections = int(new_learn_points['corrections']) \
                if new_learn_points.get('corrections') is not None else user.learn_points.corrections
            user.learn_points.transcriptions = int(new_learn_points['transcriptions']) \
                if new_learn_points.get('transcriptions') is not None else user.learn_points.transcriptions

        try:
            user.complete = True
            user.save()
            return render_json(message='Successfully updated user profile', status=200)
        except Exception as err:
            return render_json(message=err.message, status=502)

    @auth_token_required
    def delete(self):
        """
        User delete his/her own account
        """
        user = get_current_user()
        user.delete()
        # todo: delete other related data
        return render_json(message='Successfully delete account', status=200)


class UserViewResource(Resource):
    """
    User profile view
    """

    @auth_token_required
    def get(self, username):
        """
        User view other user's profile
        :param username: username
        """
        profile = User.get_other_profile(username)

        if profile is None:
            return render_json(
                message={'username': username + ' does not exist'},
                status=404
            )
        else:
            return render_json(
                message='View ' + username + "'s profile",
                status=200,
                **profile
            )


class UploadAvatar(Resource):
    """
    Upload avatar
    """

    @auth_token_required
    def put(self):
        def allowed_file(name):
            return '.' in name and \
                   name.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']

        # get current user
        user = get_current_user()

        args = uploadAvatarParse.parse_args()
        f = args['image']
        print type(f)
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            abs_name = os.path.join(current_app.config['MEDIA_ROOT'], user.username, filename)
            if not os.path.exists(os.path.dirname(abs_name)):
                try:
                    os.makedirs(os.path.dirname(abs_name))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        return render_json(message=exc.message, status=502)
            f.save(abs_name)
            user.avatar_file_path = os.path.join(user.username, filename)
            user.save()
            return render_json(message='File is saved successfully', status=200)
        return render_json(message='hello', status=400)


class UsernameResource(Resource):
    @auth_token_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        args = parser.parse_args()

        # get current user
        user = get_current_user()

        if user.username == args['username']:
            return render_json(message={'username': 'Unchanged username'}, status=304)

        if User.get_user_by_username(args['username']):
            return render_json(message={'username': 'Username has been taken'}, status=409)

        user.username = args['username']
        user.save()
        return render_json(message='Successfully change username', status=200)


class PasswordResource(Resource):
    @auth_token_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('cur_password', type=str, required=True)
        parser.add_argument('new_password', type=str, required=True)
        args = parser.parse_args()

        # get current user
        user = get_current_user()

        if not utils.verify_and_update_password(args['cur_password'], user):
            return render_json(message={'cur_password': 'Invalid password'}, status=406)

        user.set_password(args['new_password'], save=True)

        return render_json(message='Successfully change password', status=200)


class PasswordResetResource(Resource):
    def post(self):
        if not current_app.config['SECURITY_RECOVERABLE']:
            return render_json(message='Security configuration does not allow this operation', status=403)
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True)

        args = parser.parse_args()
        user = User.get_user(args['email'])

        if not user:
            return render_json(message={'email': 'User does not exist'}, status=404)

        send_reset_password_instructions(user)
        return render_json(message='Successfully send password reset instruction', status=200)


class ConfirmationRequestResource(Resource):
    def post(self):
        if not current_app.config['SECURITY_CONFIRMABLE']:
            return render_json(message='Security configuration does not allow this operation', status=403)
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True)

        args = parser.parse_args()
        user = User.get_user(args['email'])

        if not user:
            return render_json(message={'email': 'User does not exist'}, status=404)

        send_confirmation_instructions(user)
        return render_json(message='Successfully send confirmation instruction', status=200)
