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
# LoginResource:post
loginParser = reqparse.RequestParser()
loginParser.add_argument('email', type=str, required=True)
loginParser.add_argument('password', type=str, required=True)

signupParser = reqparse.RequestParser()
signupParser.add_argument('email', type=str, required=True)
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
                return render_json(message='Invalid password', status=406)
            else:
                if not user.confirmed_at:
                    return render_json(message='Please confirm your email address', status=403)
                utils.login_user(user)
                token = user.get_auth_token()
                return render_json(message='Successfully log in', status=200,
                                   auth_token=token, user_id=str(user.id),
                                   username=user.username, name=user.name,
                                   complete=user.complete)


class LogoutResource(Resource):
    def get(self):
        utils.logout_user()
        return render_json(message='Successfully log out', status=200)


class UserResource(Resource):
    """
    Sign up
    """
    def post(self):
        # parse arguments
        args = loginParser.parse_args()
        user = register_user(**args)
        return render_json(message='User has been created. You need to confirm the email to log in', status=200,
                           email=user.email)

    """
    User view him/her self
    """
    @auth_token_required
    def get(self):
        user = get_current_user()
        return render_json(message="Successfully get user's own profile",
                           status=200,
                           id=str(user.id),
                           email=user.email)

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

    @auth_token_required
    def get(self, user_id):
        return {'message': user_id}
