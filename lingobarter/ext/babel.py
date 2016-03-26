# coding: utf-8
# from flask import request, session
from flask.ext.babelex import Babel

babel = Babel()


def configure(app):
    """
    init babel
    :param app:
    :return:
    """
    babel.init_app(app)
