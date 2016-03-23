#!/usr/bin/env python
# -*- coding: utf-8 -*
from flask.ext.admin import Admin


class LingobarterAdmin(Admin):
    registered = []


def create_admin(app=None):
    return LingobarterAdmin(app)
