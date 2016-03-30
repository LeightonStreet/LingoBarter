# coding: utf-8
from flask_mail import Mail


def configure(app):
    if app.config.get('MAIL_SUPPRESS_SEND'):
        app.logger.info('Email Suppress Flag is set. Flask-Mail will not send any emails.')
    app.mail = Mail(app)
