# coding: utf-8
from flask_mail import Mail


def configure(app):
    app.mail = Mail(app)
