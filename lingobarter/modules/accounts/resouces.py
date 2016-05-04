#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import Resource, reqparse
from flask_security import utils, auth_token_required
from flask.ext.security.registerable import register_user
from lingobarter.core.json import render_json
from lingobarter.utils import get_current_user
from .models import User

"""
Parsers
=======
one can extend from another
"""
loginParser = reqparse.RequestParser()
loginParser.add_argument('email', type=str, required=True)
loginParser.add_argument('password', type=str, required=True)

signupParser = reqparse.RequestParser()
signupParser.add_argument('email', type=str, required=True)
signupParser.add_argument('name', type=str, required=True)
signupParser.add_argument('username', type=str, required=True)
signupParser.add_argument('password', type=str, required=True)


class LoginResource(Resource):
    def post(self):
        # parse arguments
        args = loginParser.parse_args()
        # get user
        user = User.get_user(email=args['email'])
        if not user:
            return render_json(message='User does not exist', status=404)
        else:
            if not utils.verify_and_update_password(args['password'], user):
                return render_json(message='Invalid password', status=403)
            else:
                if not user.confirmed_at:
                    return render_json(message='Please confirm your email address', status=403)
                utils.login_user(user)
                token = user.get_auth_token()
                return {
                    'message': 'Successfully log in',
                    'status': '200',
                    'response': {
                        'auth_token': token,
                        'user_id': str(user.id),
                        'username': user.username,
                        'name': user.name,
                        'complete': user.complete
                    }
                }


class LogoutResource(Resource):
    def get(self):
        utils.logout_user()
        return {'message': 'Successfully log out', 'status': '200'}


class UserResource(Resource):
    """
    Sign up
    """
    def post(self):
        # parse arguments
        args = loginParser.parse_args()
        user = register_user(**args)
        return {
            'message': 'User has been created. You need to confirm the email to log in',
            'status': '200',
            'response': {
                'email': user.email
            }
        }

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
            message='Get his/her own profile',
            status=200,
            response={
                'name': user.username if user.name is None else user.name,
                'tagline': user.tagline,
                'bio': user.bio,
                'teach_langs': teach_languages,
                'learn_langs': learn_languages,
                'location': {
                    'type': user.location.type,
                    'coordinates': user.location.coordinates
                },
                'birthday': user.birthday,
                'gender': user.gender,
                'nationality': user.nationality
            }
        )

    """
    User configure & update him/her self
    """
    @auth_token_required
    def put(self):
        pass

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
                message='Username: ' + username + ' does not exist.',
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

        return render_json(
            message='Get his/her own profile',
            status=200,
            response={
                'name': user.username if user.name is None else user.name,
                'tagline': user.tagline,
                'bio': user.bio,
                'teach_langs': teach_languages,
                'learn_langs': learn_languages,
                'location': {
                    'type': user.location.type,
                    'coordinates': user.location.coordinates
                },
                'birthday': user.birthday,
                'gender': user.gender,
                'nationality': user.nationality
            }
        )
