# coding: utf-8
import logging
import json
import uuid

from lingobarter.core.models.subcontent import SubContentPurpose
from lingobarter.core.models.channel import Channel, ChannelType
from lingobarter.core.models.config import Config, Lingobarter
from lingobarter.core.models.custom_values import CustomValue
from lingobarter.modules.accounts.models import User, Role

logger = logging.getLogger()


class Populate(object):
    def __init__(self, db, *args, **kwargs):
        self.db = db
        self.args = args
        self.kwargs = kwargs
        self.roles = {}
        self.users = {}
        self.channels = {}
        self.channel_types = {}
        self.purposes = {}
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
        self.create_channel_types()
        self.create_base_channels()
        self.create_channels()
        self.create_purposes()
        self.create_posts()

    def generate_random_password(self):
        return uuid.uuid4().hex

    def create_initial_superuser(self):
        password = self.generate_random_password()
        user_data = {
            "name": "Quokka Admin",
            "email": "admin@quokkaproject.org",
            "gravatar_email": "rochacbruno+quokka@gmail.com",
            "password": password[:6],
            "roles": ["admin"],
            "bio": "Quokka Example Admin",
            "tagline": "Quokka is the best CMS!",
            "links": [
                {
                    "title": "facebook",
                    "link": "http://facebook.com/quokkaproject",
                    "icon": "facebook",
                    "css_class": "facebook",
                    "order": 0
                },
                {
                    "title": "github",
                    "link": "http://github.com/quokkaproject",
                    "icon": "github",
                    "css_class": "github",
                    "order": 0
                },
                {
                    "title": "twitter",
                    "link": "http://twitter.com/quokkaproject",
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
            role, created = Role.objects.get_or_create(name=name)
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
        self.users_data = data or self.json_data.get('users')
        for data in self.users_data:
            self.create_user(data)

    @staticmethod
    def create_config(data):
        try:
            return Config.objects.get(group=data.get('group'))
        except:
            return Config.objects.create(**data)

    def custom_value(self, **data):
        if data.get('name') in self.custom_values:
            return self.custom_values[data.get('name')]

        value = CustomValue(**data)
        self.custom_values[value.name] = value
        return value

    def create_configs(self):

        self.configs_data = self.json_data.get('configs')

        for config in self.configs_data:
            config['values'] = [self.custom_value(**args)
                                for args in config.get('values')]
            self.create_config(config)

    def create_channel(self, data):

        if 'childs' in data:
            childs = data.pop('childs')
        else:
            childs = []

        data['created_by'] = data['last_updated_by'] = self.users.get('admin')
        _type = data.get('channel_type')
        data['channel_type'] = self.channel_types.get(_type)

        try:
            channel = Channel.objects.get(slug=data.get('slug'))
            created = False
        except:
            channel, created = Channel.objects.get_or_create(**data)

        if created:
            logger.info("Created channel: %s", channel.title)
        else:
            logger.info("Channel get: %s", channel.title)

        for child in childs:
            child['parent'] = channel
            self.create_channel(child)

        if channel.slug not in self.channels:
            self.channels[channel.slug] = channel

        return channel

    def create_channel_type(self, data):
        try:
            channel_type = ChannelType.objects.get(
                identifier=data.get('identifier'))
            created = False
        except:
            channel_type, created = ChannelType.objects.get_or_create(
                **data
            )

        if created:
            logger.info("Created channel_type: %s", channel_type.title)
        else:
            logger.info("ChannelType get: %s", channel_type.title)

        if channel_type.identifier not in self.channel_types:
            self.channel_types[channel_type.identifier] = channel_type

        return channel_type

    def create_base_channels(self):
        self.channel_data = self.json_data.get('base_channels')
        for data in self.channel_data:
            self.create_channel(data)

    def create_channels(self):
        self.channel_data = self.json_data.get('channels')
        for data in self.channel_data:
            self.create_channel(data)

    def create_channel_types(self):
        self.channel_type_data = self.json_data.get('channel_types')

        for data in self.channel_type_data:
            self.create_channel_type(data)

    def create_purpose(self, data):
        if data.get('identifier') in self.purposes:
            return self.purposes[data.get('identifier')]

        purpose, created = SubContentPurpose.objects.get_or_create(
            title=data.get('title'),
            identifier=data.get('identifier'),
            module=data.get('module')
        )

        self.purposes[purpose.identifier] = purpose

        return purpose

    def create_purposes(self):
        self.purpose_data = self.json_data.get('purposes')
        for purpose in self.purpose_data:
            self.create_purpose(purpose)

    def reset(self):
        SubContentPurpose.objects(
            identifier__in=[
                item['identifier'] for item in self.json_data.get('purposes')
            ]
        ).delete()

        for channel in Channel.objects(
                slug__in=[
                    item['slug'] for item in self.json_data.get('channels')]):
            for subchannel in channel.get_children():
                for subsubchannel in subchannel.get_children():
                    subsubchannel.delete()
                subchannel.delete()
            channel.delete()

        User.objects(
            email__in=[item['email'] for item in self.json_data.get('users')]
        ).delete()

        if self.kwargs.get('first_install'):
            Lingobarter.objects.delete()
