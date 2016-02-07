"""
    User Form
"""
from wtforms import Form, StringField, IntegerField, FieldList, validators


class UserForm(Form):
    nickname = StringField('nickname',
                           [validators.DataRequired(), validators.Length(max=50, message='too long nickname')])
    nationality = StringField('nationality',
                              [validators.DataRequired(), validators.Length(max=50, message='too long nationality')])
    location = StringField('location',
                           [validators.DataRequired(), validators.Length(max=50, message='too long location')])
    sex = IntegerField('sex', [validators.DataRequired(), validators.NumberRange(min=1, max=3, message='invalid sex')])
    age = IntegerField('age',
                       [validators.DataRequired(), validators.NumberRange(min=0, max=150, message='invalid age')])
    introduction = StringField('introduction',
                               [validators.DataRequired(), validators.Length(max=500, message='too long introduction')])
    teach_lan = FieldList(StringField('tech_lan', [validators.DataRequired()]),
                          [validators.Length(min=1, message='you must select at least one teaching language')])
    learn_lan = FieldList(StringField('learn_lan', [validators.DataRequired()]),
                          [validators.Length(min=1, message='you must select at least one learning language')])
