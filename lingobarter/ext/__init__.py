# coding: utf-8
from lingobarter.core.admin import configure_admin
from lingobarter.core.cache import cache
from lingobarter.core.db import db
from . import (generic, babel, blueprints, error_handlers, before_request, mail, celery_app,
               context_processors, views, fixtures, oauthlib, security, development, redis_session)


def configure_extensions(app, admin, socket_io):
    """
    configure all the extensions
    :param app:
    :param admin:
    :return:
    """
    redis_session.configure(app)
    cache.init_app(app)
    babel.configure(app)
    generic.configure(app)
    mail.configure(app)
    error_handlers.configure(app)
    db.init_app(app)
    context_processors.configure(app)
    celery_app.create_celery_app(app)
    security.configure(app, db)
    fixtures.configure(app, db)
    blueprints.load_from_folder(app, socket_io)
    configure_admin(app, admin)
    development.configure(app, admin)
    before_request.configure(app)
    views.configure(app)
    oauthlib.configure(app)
    return app


def configure_extensions_min(app, *args, **kwargs):
    db.init_app(app)
    security.configure(app, db)
    return app
