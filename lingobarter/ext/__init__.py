# coding: utf-8
from lingobarter.core.db import db
from lingobarter.core.cache import cache

from . import (blueprints, error_handlers)


def configure_extensions(app, admin):
    cache.init_app(app)
    error_handlers.configure(app)
    db.init_app(app)
    # blueprints.load_from_packages(app)
    blueprints.load_from_folder(app)
    return app


def configure_extensions_min(app, *args, **kwargs):
    db.init_app(app)
    return app
