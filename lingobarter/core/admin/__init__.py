#!/usr/bin/env python
# -*- coding: utf-8 -*
from flask.ext.admin import Admin


# default admin first
class LingobarterAdmin(Admin):
    pass


# create admin
def create_admin(app=None):
    return LingobarterAdmin(app, name='Lingobarter', template_mode='bootstrap3')


def configure_admin(app, admin):
    # routing admin
    admin_config = app.config.get(
        'ADMIN',
        {
            'name': 'Lingobarter Admin',
            'url': '/admin'
        }
    )

    for k, v in list(admin_config.items()):
        setattr(admin, k, v)

    # avoid registering twice
    if admin.app is None:
        admin.init_app(app)

    return admin
