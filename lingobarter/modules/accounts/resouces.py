#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_restful import Resource


class TodoItem(Resource):
    """
    A sample resource class
    """
    def get(self, todo_id):
        return {'task': 'Say "Hello, World!" {id}'.format(id=todo_id)}
