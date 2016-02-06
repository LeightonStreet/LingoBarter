"""
    Registration Form
"""
from wtforms import Form, StringField, PasswordField, validators


class RegistrationForm(Form):
    username = StringField('username', [validators.DataRequired()])
    email = StringField('email', [validators.DataRequired(), validators.Email(message='not a valid email')])

    password = PasswordField('password', [validators.DataRequired(),
                             validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('confirm', [validators.DataRequired()])
