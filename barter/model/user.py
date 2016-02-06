"""
    User Model
"""
from barter import db


class User(db.Document):
    username = db.StringField(required=True)
    email = db.EmailField(required=True)
    password = db.StringField(required=True)
    nickname = db.StringField(max_length=50)
    nationality = db.StringField(max_length=50)
    location = db.StringField(max_length=50)
    sex = db.BinaryField(max_bytes=2)
    age = db.IntField(min_value=0, max_value=150)
    introduction = db.StringField(max_length=500)
    teach_lan = db.ListField(field=db.StringField)
    learn_lan = db.ListField(field=db.StringField)
    profile_completed = db.BooleanField()
