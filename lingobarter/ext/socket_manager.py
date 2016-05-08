from redis import Redis
from datetime import timedelta


class SocketManager:
    def __init__(self, redis=None, prefix='socket:'):
        self.local = None
        if redis:
            self.redis = redis
        else:
            self.local = {}
        self.prefix = prefix

    def add(self, username, session_id):
        if self.local:
            self.local[username] = session_id
        else:
            self.redis.setex(self.prefix + username, session_id, int(timedelta(days=1).total_seconds()))

    def delete(self, username):
        if self.local:
            if self.local.get(username):
                del self.local[username]
        else:
            self.redis.delete(self.prefix + username)

    def get(self, username):
        if self.local:
            return self.local.get(username)
        else:
            return self.redis.get(self.prefix + username)

    def has(self, username):
        return self.get(username) is not None

    def get_all_users(self):
        """
        Get all online username list
        :return: list
        """
        if self.local:
            return self.local.keys()
        else:
            return self.redis.keys(self.prefix + '*')


def configure(app):
    redis = None
    if app.config.get('REDIS_SOCKET'):
        db = app.config.get('REDIS_SOCKET_DB') or 2
        host = app.config.get('REDIS_HOST') or 'localhost'
        port = app.config.get('REDIS_PORT') or 6379
        redis = Redis(host=host, port=port, db=db)
    app.socket_map = SocketManager(redis=redis)
