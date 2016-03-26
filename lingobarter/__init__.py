#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lingobarter.core.admin import create_admin
from lingobarter.core.app import LingobarterApp
from lingobarter.core.middleware import HTTPMethodOverrideMiddleware
from lingobarter.ext import configure_extensions

admin = create_admin()


def create_app_base(config=None, test=False, admin_instance=None, **settings):
    app = LingobarterApp('lingobarter')
    app.config.load_lingobarter_config(config=config, test=test, **settings)
    if test or app.config.get('TESTING'):
        app.testing = True
    return app


def create_app(config=None, test=False, admin_instance=None, **settings):
    app = create_app_base(
        config=config, test=test, admin_instance=admin_instance, **settings
    )

    configure_extensions(app, admin_instance or admin)
    if app.config.get("HTTP_PROXY_METHOD_OVERRIDE"):
        app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)
    return app


def create_api(config=None, **settings):
    return None
