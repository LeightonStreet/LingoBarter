#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lingobarter.core.admin import create_admin
from lingobarter.core.app import LingobarterApp
from lingobarter.core.middleware import HTTPMethodOverrideMiddleware
from lingobarter.ext import configure_extensions

admin = create_admin()


def create_app_base(config=None, test=False, **settings):
    """
    create basic app. no extension added to app object
    in this function.
    :param config:
    :param test:
    :param settings:
    :return:
    """
    app = LingobarterApp('lingobarter')
    app.config.load_lingobarter_config(config=config, test=test, **settings)
    if test or app.config.get('TESTING'):
        app.testing = True
    return app


def create_app(config=None, test=False, admin_instance=None, **settings):
    """
    use create_app_base, and configure extensions here.
    admin is added in this function. The routing policy
    is `/admin`.
    :param config:
    :param test:
    :param admin_instance:
    :param settings:
    :return:
    """
    app = create_app_base(
        config=config, test=test, **settings
    )
    # configure all the extensions
    configure_extensions(app, admin_instance or admin)
    # http method override, by query params or headers
    if app.config.get("HTTP_PROXY_METHOD_OVERRIDE"):
        app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)
    return app
