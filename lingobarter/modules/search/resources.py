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
searchParser.add_argument('teach_langs', type=list, required=True)
searchParser.add_argument('learn_langs', type=list, required=True)


class SearchResource(Resource):
    @auth_token_required
    def post(self):
        pass
