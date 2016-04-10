# -*- coding: utf-8 -*

from flask_restful import Api


# default api first
from lingobarter.core.app import LingobarterModule


class LingobarterApi(Api):
    """
    The Lingobarter Api class.
    You need to initialize it with each Flask Blueprint object.

    >>> module = LingobarterModule('name', __name__)
    >>> api = LingobarterApi(module)

    :param app: the Flask Blueprint object
    :type app: flask.Blueprint
    :param version: the version of api, will prefix all routes
    :type version: str
    """
    def __init__(self, app, version):
        """
        Add name to the class, name equals to module_name.api.version
        set prefix of Api, prefix equals to api/version
        :param app:
        :param version:
        :return:
        """
        self.name = 'api.' + str(version)
        super(LingobarterApi, self).__init__(app=app, prefix='/api/' + str(version), catch_all_404s=True)

    def add_lingobarter_resource(self, resource, *urls, **kwargs):
        endpoint = kwargs.get('endpoint', None)
        if endpoint is None:
            endpoint = self.name + '.' + resource.__name__.lower()
        if not endpoint.startswith(self.name):
            endpoint = self.name + '.' + endpoint
        kwargs['endpoint'] = endpoint
        self.add_resource(resource, *urls, **kwargs)
