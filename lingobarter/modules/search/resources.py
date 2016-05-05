#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import Resource, reqparse
from flask_security import auth_token_required


"""
Parsers
=======
one can extend from another
"""
searchParser = reqparse.RequestParser()
searchParser.add_argument('age_range', type=list, required=False)
searchParser.add_argument('nationality', type=str, required=False) # list of string
searchParser.add_argument('teach_langs', type=list, required=True)
searchParser.add_argument('learn_langs', type=list, required=True)
searchParser.add_argument('has_bio', type=bool, required=False)

# in database: teach_langs i want to teach ..., learn_langs is want to learn

class SearchResource(Resource):
    @auth_token_required
    def post(self):
        # parse arguments
        args = searchParser.parse_args()

        # response: list:
        # /users/<userid> get
        # 20 users per page
        # skip, limit

