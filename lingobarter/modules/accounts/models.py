#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from random import randint

from bson.objectid import ObjectId
from flask import url_for
from flask.ext.security import UserMixin, RoleMixin
from flask.ext.security.utils import encrypt_password
from flask_gravatar import Gravatar
from lingobarter.core.db import db
from lingobarter.core.models.custom_values import HasCustomValue
from lingobarter.utils import dateformat
from lingobarter.utils.text import abbreviate, slugify

logger = logging.getLogger()


# Auth
class Role(db.Document, HasCustomValue, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)

    @classmethod
    def createrole(cls, name, description=None):
        return cls.objects.create(
            name=name,
            description=description
        )

    def __unicode__(self):
        return u"{0} ({1})".format(self.name, self.description or 'Role')


class UserLink(db.EmbeddedDocument):
    title = db.StringField(max_length=50, required=True)
    link = db.StringField(max_length=255, required=True)
    icon = db.StringField(max_length=255)
    css_class = db.StringField(max_length=50)
    order = db.IntField(default=0)

    def __unicode__(self):
        return u"{0} - {1}".format(self.title, self.link)


class LanguageItem(db.EmbeddedDocument):
    language_id = db.StringField(max_length=50, required=True)
    level = db.IntField(default=0)

    def __unicode__(self):
        return u"{0} - {1}".format(self.language_id, self.level)


class Location(db.EmbeddedDocument):
    type = db.StringField(
        choices=(
            ("Point", "Point"),
            ("Polygon", "Polygon"),
            ("LineString", "LineString")
        ),
        default='Point')
    coordinates = db.ListField(db.FloatField(), default=[])

    def __unicode__(self):
        return u"{0} - {1}".format(self.type, self.coordinates)


class Place(db.DynamicDocument, HasCustomValue):
    country_code = db.StringField(max_length=5, required=True)
    country = db.StringField(max_length=50, required=True)
    place_type = db.StringField(
        choices=(
            ('city', 'city'),
            ('region', 'region')
        ),
        max_length=20,
        default='city'
    )
    location = db.EmbeddedDocumentField(Location)
    full_name = db.StringField(max_length=100)
    name = db.StringField(max_length=50)

    def __unicode__(self):
        return u"{0} - {1}".format(self.country_code, self.country)


class UserSetting(db.EmbeddedDocument):
    strict_lang_match = db.BooleanField(default=False)
    same_gender = db.BooleanField(default=False)
    age_range = db.ListField(db.IntField(), default=[14, 90])
    hide_from_nearby = db.BooleanField(default=False)
    hide_from_search = db.BooleanField(default=False)
    hide_info_fields = db.ListField(db.StringField(), default=[])
    partner_confirmation = db.BooleanField(default=True)

    def __unicode__(self):
        return u"{0} - {1} - {2} - {3} - {4} - {5} - {6}".format(self.strict_lang_match, self.same_gender,
                                                                 self.age_range, self.hide_from_nearby,
                                                                 self.hide_from_search, self.hide_info_fields,
                                                                 self.partner_confirmation)


class LearnPoint(db.EmbeddedDocument):
    favorites = db.IntField(default=0)
    pronunciations = db.IntField(default=0)
    translations = db.IntField(default=0)
    transliterations = db.IntField(default=0)
    corrections = db.IntField(default=0)
    transcriptions = db.IntField(default=0)

    def __unicode__(self):
        return u"{0} - {1} - {2} - {3} - {4} - {5}".format(self.favorites, self.pronunciations,
                                                           self.translations, self.transliterations,
                                                           self.corrections, self.transcriptions)


class User(db.DynamicDocument, HasCustomValue, UserMixin):
    name = db.StringField(max_length=255)
    email = db.EmailField(max_length=255, required=True, unique=True)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    complete = db.BooleanField(default=False)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(
        db.ReferenceField(Role, reverse_delete_rule=db.DENY), default=[]
    )

    last_login_at = db.DateTimeField()
    current_login_at = db.DateTimeField()
    last_login_ip = db.StringField(max_length=255)
    current_login_ip = db.StringField(max_length=255)
    login_count = db.IntField()

    username = db.StringField(max_length=50, required=True, unique=True)

    remember_token = db.StringField(max_length=255)
    authentication_token = db.StringField(max_length=255)

    tagline = db.StringField(max_length=255)
    bio = db.StringField()
    links = db.ListField(db.EmbeddedDocumentField(UserLink))

    use_avatar_from = db.StringField(
        choices=(
            ("gravatar", "gravatar"),
            ("url", "url"),
            ("upload", "upload"),
            ("facebook", "facebook")
        ),
        default='upload'
    )
    gravatar_email = db.EmailField(max_length=255)
    avatar_file_path = db.StringField()
    avatar_url = db.StringField(max_length=255)
    teach_langs = db.ListField(db.EmbeddedDocumentField(LanguageItem), default=[])
    learn_langs = db.ListField(db.EmbeddedDocumentField(LanguageItem), default=[])
    location = db.EmbeddedDocumentField(Location)
    place = db.ReferenceField(Place, reverse_delete_rule=db.DENY)
    birthday = db.DateTimeField()
    gender = db.StringField(
        choices=(
            ("male", "male"),
            ("female", "female"),
            ("unknown", "unknown")
        ),
        default="unknown",
        required=True
    )
    settings = db.EmbeddedDocumentField(UserSetting, default=UserSetting())
    learn_points = db.EmbeddedDocumentField(LearnPoint, default=LearnPoint())
    nationality = db.StringField()
    partners = db.ListField(db.ObjectIdField(), default=[])

    def has_partner(self, user_id):
        if type(user_id) != ObjectId:
            user_id = ObjectId(user_id)
        return user_id in self.partners

    def add_partner(self, user_id):
        if type(user_id) != ObjectId:
            user_id = ObjectId(user_id)
        if user_id in self.partners:
            return
        self.partners.append(user_id)
        self.save()

    def get_avatar_url(self, *args, **kwargs):
        if self.use_avatar_from == 'url':
            return self.avatar_url
        elif self.use_avatar_from == 'upload':
            return url_for(
                'lingobarter.core.media', filename=self.avatar_file_path
            )
        elif self.use_avatar_from == 'facebook':
            try:
                return Connection.objects(
                    provider_id='facebook',
                    user_id=self.id,
                ).first().image_url
            except Exception as e:
                logger.warning(
                    '%s use_avatar_from is set to facebook but: Error: %s' % (
                        self.display_name, str(e)
                    )
                )
        return Gravatar()(
            self.get_gravatar_email(), *args, **kwargs
        )

    @property
    def summary(self):
        return (self.bio or self.tagline or '')[:255]

    def get_gravatar_email(self):
        return self.gravatar_email or self.email

    def clean(self, *args, **kwargs):
        if not self.username:
            self.username = User.generate_username(self.name)
        super(User, self).clean(*args, **kwargs)

    @classmethod
    def generate_username(cls, name, user=None):
        name = name or ''
        username = slugify(name)
        filters = {"username": username}
        if user:
            filters["id__ne"] = user.id
        if cls.objects.filter(**filters).count():
            username = "{0}{1}".format(username, randint(1, 1000))
        return username

    def set_password(self, password, save=False):
        self.password = encrypt_password(password)
        if save:
            self.save()

    @classmethod
    def createuser(cls, name, email, password,
                   active=True, roles=None, username=None,
                   *args, **kwargs):

        username = username or cls.generate_username(name)
        if 'links' in kwargs:
            kwargs['links'] = [UserLink(**link) for link in kwargs['links']]

        return cls.objects.create(
            name=name,
            email=email,
            password=encrypt_password(password),
            active=active,
            roles=roles,
            username=username,
            *args,
            **kwargs
        )

    @property
    def display_name(self):
        return abbreviate(self.name) or self.email

    def __unicode__(self):
        return u"{0} <{1}>".format(self.name or '', self.email)

    @property
    def connections(self):
        return Connection.objects(user_id=str(self.id))

    @classmethod
    def get_user(cls, email):
        return cls.objects(email=email).first()

    @classmethod
    def get_user_by_username(cls, username):
        return cls.objects(username=username).first()

    @classmethod
    def get_user_by_id(cls, user_id):
        if type(user_id) != ObjectId:
            user_id = ObjectId(user_id)
        return cls.objects(_id=user_id).first()

    @classmethod
    def get_other_simplified_profile(cls, username=None, user_id=None):
        """
        get simplified profile by username or id
        :param username:
        :param user_id:
        :return:
        """
        if username:
            user = User.get_user_by_username(username)
        elif user_id:
            user = User.get_user_by_id(user_id)
        else:
            return None

        if user is None:
            return None

        profile = {
            'id': str(user.id),
            'name': user.username if user.name is None else user.name,
            'username': user.username,
            'avatar_url': user.get_avatar_url() if user.avatar_file_path is not None else None
        }

        return profile

    @classmethod
    def get_other_profile(cls, username=None, user_id=None):
        """
        get profile by username or id
        :param user_id:
        :param username:
        """
        if username:
            user = User.get_user_by_username(username)
        elif user_id:
            user = User.get_user_by_id(user_id)
        else:
            return None

        if user is None:
            return None

        teach_languages = []
        learn_languages = []

        for tech_language in user.teach_langs:
            teach_languages.append({
                'language_id': tech_language.language_id,
                'level': tech_language.level
            })

        for learn_language in user.learn_langs:
            learn_languages.append({
                'language_id': learn_language.language_id,
                'level': learn_language.level
            })

        # could be ['location', 'nationality', 'birthday', 'current_login_at', 'gender']
        invisible_fields = user.settings.hide_info_fields

        profile = {
            'id': str(user.id),
            'name': user.username if user.name is None else user.name,
            'username': user.username,
            'tagline': user.tagline,
            'bio': user.bio,
            'avatar_url': user.get_avatar_url() if user.avatar_file_path is not None else None,
            'teach_langs': teach_languages,
            'learn_langs': learn_languages,
            'location': {'type': user.location.type, 'coordinates': user.location.coordinates}
            if user.location and 'location' not in invisible_fields else None,
            'birthday': dateformat.datetime_to_timestamp(user.birthday)
            if 'birthday' not in invisible_fields else None,
            'gender': user.gender if 'gender' not in invisible_fields else None,
            'nationality': user.nationality if 'nationality' not in invisible_fields else None,
            'current_login_at': dateformat.datetime_to_timestamp(user.current_login_at)
            if 'current_login_at' not in invisible_fields else None
        }

        return profile


class Connection(db.Document):
    user_id = db.ObjectIdField()
    provider_id = db.StringField(max_length=255)
    provider_user_id = db.StringField(max_length=255)
    access_token = db.StringField(max_length=255)
    secret = db.StringField(max_length=255)
    display_name = db.StringField(max_length=255)
    full_name = db.StringField(max_length=255)
    profile_url = db.StringField(max_length=512)
    image_url = db.StringField(max_length=512)
    rank = db.IntField(default=1)

    @property
    def user(self):
        return User.objects(id=self.user_id).first()

    def __unicode__(self):
        return u"{0}".format(self.user_id)


class Language(db.DynamicDocument):
    name = db.StringField(max_length=50, required=True, unique=True)
    u_name = db.StringField(max_length=100)
    abbrev = db.StringField(max_length=10, required=True)

    def __unicode__(self):
        return u"{0} - {1} - {2}".format(self.name, self.u_name, self._id)
