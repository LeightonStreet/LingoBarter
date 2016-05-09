#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from bson.objectid import ObjectId
from lingobarter.core.db import db
from lingobarter.core.models.custom_values import HasCustomValue


class Chat(db.DynamicDocument, HasCustomValue):
    # todo: the name of chat will be ignored if it is a p2p chat
    # todo: and will be several users' username by default if it is a group chat
    name = db.StringField(max_length=50, required=True)
    members = db.ListField(db.ObjectIdField(), default=[])
    last_updated = db.DateTimeField(default=datetime.now())

    @classmethod
    def get_chat_by_id(cls, chat_id):
        if type(chat_id) != ObjectId:
            chat_id = ObjectId(chat_id)
        return cls.objects(_id=chat_id).first()

    def __unicode__(self):
        return u"{0} - {1}".format(self.name, self._id)


class Message(db.DynamicDocument, HasCustomValue):
    from_id = db.ObjectIdField(required=True)
    to_chat = db.ObjectIdField(required=True)
    type = db.StringField(
        choices=(
            ("text", "text"),
            ("voice", "voice"),
            ("image", "image")
        ),
        default='text', required=True)
    voice_file_path = db.StringField()
    text_content = db.StringField()
    image_file_path = db.StringField()
    undelivered = db.ListField(db.ObjectIdField(), default=[])
    # todo: default time->now
    timestamp = db.DateTimeField(default=datetime.now())

    def __unicode__(self):
        return u"{0} - {1} - {2} - {3}".format(self.from_id, self.to_chat, self.type, self.timestamp)


class PartnerRequest(db.DynamicDocument, HasCustomValue):
    from_id = db.ObjectIdField(required=True)
    to_id = db.ObjectIdField(required=True)
    # todo: default time->now
    timestamp = db.DateTimeField(default=datetime.now())
    status = db.StringField(
        choices=(
            ("pending", "pending"),
            ("added", "added"),
            ("rejected", "rejected"),
            ("outdated", "outdated")
        ),
        default='pending', required=True)

    def __unicode__(self):
        return u"{0} - {1} - {2} - {3}".format(self.from_id, self.to_id, self.timestamp, self.status)

