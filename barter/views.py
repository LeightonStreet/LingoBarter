from barter import app
from flask import render_template, redirect, url_for, session
from barter.model import *
from barter.db import *
from hashlib import md5
from flask import request


@app.route('/')
def index():
    if not session.get('username'):
        return redirect(url_for('login'))
    else:
        return render_template('index.html', users=fetch_all_users())


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        form = LoginForm(request.form)
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


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    error = None
    if request.method == 'POST':
        form = RegistrationForm(request.form)
        m = md5()
        m.update(form.password.data)
        ret, error = signup_user(email=form.email.data, password=m.hexdigest(), username=form.username.data)
        if ret:
            session['username'] = form.username.data
            return redirect(url_for('index'))
    return render_template('signup.html', error=error)


@app.route('/logout')
def logout():
    del session['username']
    return redirect('login')


@app.route('/<username>', methods=['POST', 'GET'])
def homepage(username):
    if not session.get('username'):
        return redirect('login')
    error = None
    u = None
    if request.method == 'POST':
        form = UserForm(request.form)
        u = update_user(nickname=form.nickname.data,
                        nationality=form.nationality.data,
                        location=form.location.data,
                        sex=form.sex.data,
                        age=form.age.data,
                        introduction=form.introduction.data,
                        teach_lan=form.teach_lan.data,
                        learn_lan=form.learn_lan.data,
                        username=session['username'])
        if u:
            error = "Update successfully"
        else:
            error = "Error occurred"
    return render_template('user.html', error=error, user=u)
