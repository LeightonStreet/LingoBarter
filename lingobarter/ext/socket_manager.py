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

    def add(self, user_id, session_id):
        user_id = str(user_id)
        if self.local is not None:
            self.local[user_id] = session_id
        else:
            self.redis.setex(self.prefix + user_id, session_id, int(timedelta(days=1).total_seconds()))

    def delete(self, user_id):
        user_id = str(user_id)
        if self.local is not None:
            if self.local.get(user_id):
                del self.local[user_id]
        else:
            self.redis.delete(self.prefix + user_id)

    def get(self, user_id):
        user_id = str(user_id)
        if self.local is not None:
            return self.local.get(user_id)
        else:
            return self.redis.get(self.prefix + user_id)

    def has(self, user_id):
        user_id = str(user_id)
        return self.get(user_id) is not None

    def get_all_users(self):
        """
        Get all online user_id list
        :return: list
        """
        if self.local is not None:
            return self.local.keys()
        else:
            return [user.strip(self.prefix) for user in self.redis.keys(self.prefix + '*')]


def configure(app):
    redis = None
    if app.config.get('REDIS_SOCKET'):
        db = app.config.get('REDIS_SOCKET_DB') or 2
        host = app.config.get('REDIS_HOST') or 'localhost'
        port = app.config.get('REDIS_PORT') or 6379
        redis = Redis(host=host, port=port, db=db)
    app.socket_map = SocketManager(redis=redis)
