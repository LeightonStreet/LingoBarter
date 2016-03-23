from flask import Flask, Blueprint
from flask.helpers import _endpoint_from_view_func
from lingobarter.core.config import LingobarterConfig


class LingobarterApp(Flask):
    """
    Implementes customizations on Flask
    - Config handler
    - Aliases dispatching before request
    """

    config_class = LingobarterConfig

    def make_config(self, instance_relative=False):
        """This method should be removed when Flask is >=0.11
        :param instance_relative:
        """
        root_path = self.root_path
        if instance_relative:
            root_path = self.instance_path
        return self.config_class(root_path, self.default_config)

    def preprocess_request(self):
        return super(LingobarterApp, self).preprocess_request()

    def add_lingobarter_url_rule(self, rule, endpoint=None, view_func=None, **options):
        if endpoint is None:
            endpoint = _endpoint_from_view_func(view_func)
        if not endpoint.startswith('lingobarter.'):
            endpoint = 'lingobarter.core.' + endpoint
        self.add_url_rule(rule, endpoint, view_func, **options)


class LingobarterModule(Blueprint):
    """Overwrite blueprint namespace to lingobarter.modules.name"""

    def __init__(self, name, *args, **kwargs):
        name = "lingobarter.modules." + name
        super(LingobarterModule, self).__init__(name, *args, **kwargs)
