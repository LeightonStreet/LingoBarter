#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_restful import Resource
from lingobarter.utils import get_current_user
import json
from bson import json_util
from flask import request


class LoginResource(Resource):
    def post(self):
        pass

class LogoutResource(Resource):
    def post(self):
        pass


class SignupResource(Resource):
    def post(self):
        pass


class UserResource(Resource):
    # get user profile
    def get(self, user_id):
        current_user = get_current_user()
        if user_id == current_user.get_id():
            return json.dumps(current_user, default=json_util.default)
        else:
            pass

    def post(self):
        form = self.form(request.form)
        if form.validate():
            user = get_current_user()
            # todo: update fields
            user.save()
