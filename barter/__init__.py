"""
    The __init__ file for package barter
"""
from flask import Flask

__author__ = "He Li"

app = Flask(__name__)

import barter.views
