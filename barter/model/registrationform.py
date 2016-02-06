"""
    Registration Form
"""
from wtforms import Form, StringField, PasswordField, validators


class RegistrationForm(Form):
    username = StringField('username', validators.DataRequired())
    email = StringField('email', validators.DataRequired())
    password = PasswordField('password', validators.DataRequired(),
                             validators.EqualTo('confirm', message='Passwords must match'))
    confirm = PasswordField('repeat password', validators.DataRequired())
