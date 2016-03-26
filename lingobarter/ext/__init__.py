# coding: utf-8
from flask_mail import Mail
from lingobarter.core.cache import cache
from lingobarter.core.db import db
from lingobarter.core.admin import configure_admin
from . import (generic, babel, blueprints, error_handlers, before_request,
               views, fixtures, oauthlib, security, development)


def configure_extensions(app, admin):
    cache.init_app(app)
    babel.configure(app)
    generic.configure(app)
    Mail(app)
    error_handlers.configure(app)
    db.init_app(app)
    security.configure(app, db)
    fixtures.configure(app, db)
    blueprints.load_from_folder(app)
    configure_admin(app, admin)
    development.configure(app, admin)
    before_request.configure(app)
    views.configure(app)
    oauthlib.configure(app)
    return app


def configure_extensions_min(app, *args, **kwargs):
    db.init_app(app)
    security.init_app(app, db)
    return app
