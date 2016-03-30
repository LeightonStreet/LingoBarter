# coding: utf-8
from celery import Celery


def create_celery_app(app):
    if app.config.get('CELERY_ENABLED'):
        app.celery = Celery(__name__, broker=app.config['CELERY_BROKER_URL'])
        app.celery.conf.update(app.config)
        taskbase = app.celery.Task

        class ContextTask(taskbase):
            abstract = True

            # make it within flask context
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return taskbase.__call__(self, *args, **kwargs)

        app.celery.Task = ContextTask
