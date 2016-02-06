from barter import app
from flask import render_template, redirect, url_for, session
from barter.model import *
from barter.db import *
from hashlib import md5
from flask import request


@app.route('/')
def index():
    return str([u.username for u in fetch_all_users()]) + session['username']


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        m = md5()
        m.update(form.password.data)
        u = User.objects(email=form.email.data, password=m.hexdigest())
        if len(u) == 0:
            error = 'incorrect username or password'
        else:
            u = u[0]
            session['username'] = u.username
            return redirect(url_for('index'))
    return render_template('login.html', error=error)


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
