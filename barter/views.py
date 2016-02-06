from barter import app
# from flask import render_template
from barter.db import *

from flask import request


@app.route('/')
def index():
    return str([u.username for u in fetch_all_users()])


@app.route('/login')
def login():
    pass


@app.route('/signup')
def signup():
    succeed = signup_user(email=request.args.get('email'),
                          username=request.args.get('username'),
                          password=request.args.get('password'))
    return str(succeed)


@app.route('/logout')
def logout():
    pass


@app.route('/<username>')
def homepage():
    pass
