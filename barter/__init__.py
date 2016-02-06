"""
    The __init__ file for package barter
"""
from flask import Flask
from flask.ext.mongoengine import MongoEngine

__author__ = "He Li"

# connect to the database
db = MongoEngine()
# make our app object
app = Flask(__name__)
# config the database
app.config['MONGODB_SETTINGS'] = {
    'db': 'lingobarter',
    'host': '127.0.0.1',
    'port': 27017
}
db.init_app(app)

import barter.views






