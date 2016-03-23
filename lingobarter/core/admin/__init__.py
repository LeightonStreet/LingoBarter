#!/usr/bin/env python
# -*- coding: utf-8 -*
from flask.ext.admin import Admin


# default admin first
class LingobarterAdmin(Admin):
    pass


# create admin
def create_admin(app=None):
    return LingobarterAdmin(app, name='Lingobarter', template_mode='bootstrap3')
