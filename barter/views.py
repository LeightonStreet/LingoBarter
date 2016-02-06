from barter import app
from flask import render_template
from barter.model import User


@app.route('/')
def index():
    User(username='lihe', nickname='He Li', avatar='nothing').save()
    return render_template('login.html')

