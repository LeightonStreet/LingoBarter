#!/usr/bin/env python
# -*- coding: utf-8 -*
from flask import request, session
from flask.ext.admin import Admin


# default admin first
class LingobarterAdmin(Admin):
    pass


# create admin
def create_admin(app=None):
    return LingobarterAdmin(app, name='Lingobarter', template_mode='bootstrap3')


def configure_admin(app, admin):
    admin_config = app.config.get(
        'ADMIN',
        {
            'name': 'Lingobarter Admin',
            'url': '/admin'
        }
    )

    for k, v in list(admin_config.items()):
        setattr(admin, k, v)

    babel = app.extensions.get('babel')
    if babel:
        try:
            @babel.localeselector
            def get_locale():
                # use default language if set
                if app.config.get('BABEL_DEFAULT_LOCALE'):
                    session['lang'] = app.config.get('BABEL_DEFAULT_LOCALE')
                else:
                    # get best matching language
                    if app.config.get('BABEL_LANGUAGES'):
                        session['lang'] = request.accept_languages.best_match(
                            app.config.get('BABEL_LANGUAGES')
                        )

                return session.get('lang', 'en')

            admin.locale_selector(get_locale)
        except Exception as e:
            app.logger.info('Cannot add locale_selector. %s' % e)

    # avoid registering twice
    if admin.app is None:
        admin.init_app(app)

    return admin
