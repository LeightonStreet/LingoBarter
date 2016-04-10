# coding: utf-8

from flask.ext.mistune import Mistune
from flask_wtf.csrf import CsrfProtect


def configure(app):
    """
    configure mistune, csrf, and gravatar
    :param app:
    :return:
    """
    Mistune(app)
    # TODO: shutdown csrf protection for now
    # CsrfProtect(app)
    if app.config.get('GRAVATAR'):
        from flask.ext.gravatar import Gravatar
        Gravatar(app, **app.config.get('GRAVATAR'))
