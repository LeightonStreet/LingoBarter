import logging
from flask import current_app, request
from lingobarter.core.db import db
from lingobarter.core.app import LingobarterApp

logger = logging.getLogger()


def create_app_min(config=None, test=False):
    app = LingobarterApp('lingobarter')
    app.config.load_lingobarter_config(config=config, test=test)
    return app


def get_setting_value(key, default=None):
    try:
        return current_app.config.get(key, default)
    except RuntimeError as e:
        logger.warning('current_app is inaccessible: %s' % e)

    try:
        app = create_app_min()
        db.init_app(app)
        with app.app_context():
            return app.config.get(key, default)
    except:
        return default


def get_password(f):
    try:
        return open('.%s_password.txt' % f).read().strip()
    except:
        return
