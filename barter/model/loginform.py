from wtforms import Form, StringField, PasswordField, validators


class LoginForm(Form):
    email = StringField('email', [validators.Length(min=6, max=35), validators.DataRequired()])
    password = PasswordField('New Password', [validators.DataRequired()])
