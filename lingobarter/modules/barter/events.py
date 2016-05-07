import functools

from flask.ext.security.decorators import _check_token
from flask_socketio import disconnect
from flask_socketio import emit


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not _check_token():
            disconnect()
        else:
            return f(*args, **kwargs)

    return wrapped


def register_events(socket_io):
    # get my self
    @socket_io.on('me')
    @authenticated_only
    def me():
        emit('me', {'message': 'hello!!'})
