# coding: utf-8
import json
import logging
import uuid

from lingobarter.core.models.config import Config, Lingobarter
from lingobarter.core.models.custom_values import CustomValue
from lingobarter.modules.accounts.models import User, Role
from mongoengine import DoesNotExist

logger = logging.getLogger()


class Populate(object):
    def __init__(self, db, *args, **kwargs):
        self.db = db
        self.args = args
        self.kwargs = kwargs
        self.json_data = None
        self.roles = {}
        self.users = {}
        self.custom_values = {}
        self.load_fixtures()
        self.baseurl = self.kwargs.get('baseurl')
        self.app = self.kwargs.get('app')

    def __call__(self, *args, **kwargs):
        if self.baseurl and self.app:
            with self.app.test_request_context(base_url=self.baseurl):
                self.pipeline()
        else:
            self.pipeline()

    def pipeline(self):
        self.load_existing_users()
        self.create_users()
        self.create_configs()

    @staticmethod
    def generate_random_password():
        return uuid.uuid4().hex

    def create_initial_superuser(self):
        password = self.generate_random_password()
        user_data = {
            "name": "Lingobarter Admin",
            "email": "admin@lingobarter.com",
            "gravatar_email": "jet.in.brain@gmail.com",
            "password": password[:6],
            "roles": ["admin"],
            "bio": "Lingobarter Example Admin",
            "tagline": "Lingobarter is the best language exchange platform!",
            "links": [
                {
                    "title": "facebook",
                    "link": "http://facebook.com/lingobarter",
                    "icon": "facebook",
                    "css_class": "facebook",
                    "order": 0
                },
                {
                    "title": "github",
                    "link": "http://github.com/lingobarter",
                    "icon": "github",
                    "css_class": "github",
                    "order": 0
                },
                {
                    "title": "twitter",
                    "link": "http://twitter.com/lingobarter",
                    "icon": "twitter",
                    "css_class": "twitter",
                    "order": 0
                }
            ]
        }
        user_obj = self.create_user(user_data)
        return user_data, user_obj

    def load_fixtures(self):
        filepath = self.kwargs.get('filepath',
                                   './etc/fixtures/initial_data.json')
        _file = open(filepath)
        self.json_data = json.load(_file)

    def role(self, name):
        if name not in self.roles:
            try:
                role = Role.objects.get(name=name)
                created = False
            except DoesNotExist:
                # noinspection PyArgumentList
                role = Role(name=name,
                            description='role created by population')
                role.save()
                created = True
            self.roles[name] = role
            if created:
                logger.info("Created role: %s", name)
        return self.roles.get(name)

    def load_existing_users(self):
        users = User.objects.all()
        for user in users:
            self.users[user.name] = user

    def create_user(self, data):
        name = data.get('name')
        if name not in self.users:
            pwd = data.get("password")
            data['roles'] = [self.role(role) for role in data.get('roles')]
            user = User.createuser(**data)
            self.users[name] = user
            logger.info("Created: User: mail:%s pwd:%s", user.email, pwd)
            return user
        else:
            logger.info("Exist: User: mail: %s", data.get('email'))

    def create_users(self, data=None):
        users_data = data or self.json_data.get('users')
        for data in users_data:
            self.create_user(data)

    @staticmethod
    def create_config(data):
        try:
            return Config.objects.get(group=data.get('group'))
        except DoesNotExist:
            return Config.objects.create(**data)

    def custom_value(self, **data):
        if data.get('name') in self.custom_values:
            return self.custom_values[data.get('name')]

        value = CustomValue(**data)
        self.custom_values[value.name] = value
        return value

    def create_configs(self):
        configs_data = self.json_data.get('configs')

        for config in configs_data:
            config['values'] = [self.custom_value(**args)
                                for args in config.get('values')]
            self.create_config(config)

    def reset(self):
        User.objects(
            email__in=[item['email'] for item in self.json_data.get('users')]
        ).delete()

        if self.kwargs.get('first_install'):
            Lingobarter.objects.delete()
