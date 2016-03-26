import logging

import lingobarter.core.models as m
import os
from cached_property import cached_property, cached_property_ttl
from flask.config import Config
from lingobarter.utils import parse_conf_data

logger = logging.getLogger()


class LingobarterConfig(Config):
    """A Config object for Flask that tries to ger vars from
    database and then from Config itself"""

    @cached_property
    def store(self):
        return dict(self)

    @cached_property_ttl(300)
    def all_setings_from_db(self):
        """
        As config reads data from database on every app.config.get(key)/[key]
        This data is cached as a cached_property
        The TTL is fixed in 5 minutes because we can't read it from
        config itself.
        Find a way to set the config parameter in a file
        maybe in a config_setting.ini
        It takes 5 minutes for new values to be available
        and Make it possible to use REDIS as a cache
        """
        try:
            return {
                item.name: item.value
                for item in m.config.Config.objects.get(
                    group='settings'
                ).values
            }
        except Exception as e:
            logger.warning('Error reading all settings from db: %s' % e)
            return {}

    def get_from_db(self, key, default=None):
        return self.all_setings_from_db.get(key, default)

    def __getitem__(self, key):
        return self.get_from_db(key) or dict.__getitem__(self, key)

    def get(self, key, default=None):
        return self.get_from_db(key) or self.store.get(key) or default

    def from_object(self, obj, silent=False):
        try:
            super(LingobarterConfig, self).from_object(obj)
        except ImportError as e:
            if silent:
                return False
            e.message = 'Unable to load configuration obj (%s)' % e.message
            raise

    def from_envvar_namespace(self, namespace='LINGOBARTER', silent=False):
        try:
            data = {
                key.partition('_')[-1]: parse_conf_data(data)
                for key, data
                in os.environ.items()
                if key.startswith(namespace)
                }
            self.update(data)
        except Exception as e:
            if silent:
                return False
            e.message = 'Unable to load config env namespace (%s)' % e.message
            raise

    def load_lingobarter_config(self, config=None, mode=None, test=None, **sets):
        # first load from global settings object
        self.from_object(config or 'lingobarter.settings')
        # then load from local or test settings
        mode = mode or 'test' if test else os.environ.get(
            'LINGOBARTER_MODE', 'local')
        self.from_object('lingobarter.%s_settings' % mode, silent=True)
        path = "LINGOBARTER_SETTINGS" if not test else "LINGOBARTERTEST_SETTINGS"
        self.from_envvar(path, silent=True)
        self.from_envvar_namespace(namespace='LINGOBARTER', silent=True)
        self.update(sets)
