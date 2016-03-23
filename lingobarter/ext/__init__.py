# coding: utf-8
from flask_mail import Mail

from lingobarter.core.db import db
from lingobarter.core.cache import cache

from . import (blueprints, error_handlers, views)


def configure_extensions(app, admin):
    cache.init_app(app)
    Mail(app)
    error_handlers.configure(app)
    db.init_app(app)
    blueprints.load_from_folder(app)
    views.configure(app)
    return app


def configure_extensions_min(app, *args, **kwargs):
    db.init_app(app)
    return app
