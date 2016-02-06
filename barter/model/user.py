"""
    User Model
"""
from barter import db


class User(db.Document):
    username = db.StringField(required=True)
    nickname = db.StringField(max_length=50)
    avatar = db.StringField(max_length=50)
