from flask_socketio import emit


def register_events(socket_io):
    # get my self
    @socket_io.on('me')
    def me():
        emit('me', {'message': 'hello!!'})
