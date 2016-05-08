import functools

from bson.objectid import ObjectId
from flask import current_app, request
from flask.ext.security import current_user
from flask.ext.security.decorators import _check_token
from flask_socketio import disconnect
from flask_socketio import emit
from lingobarter.core.json import render_json
from lingobarter.modules.accounts.models import User
from lingobarter.utils.dateformat import datetime_to_timestamp
from .models import PartnerRequest, Chat


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not _check_token():
            disconnect()
        else:
            return f(*args, **kwargs)

    return wrapped


def register_events(socket_io):
    @socket_io.on('connect')
    @authenticated_only
    def handle_connect():
        current_app.socket_map.add(current_user.username, request.sid)
        emit('connected', render_json(message='connected', status=200))

    @socket_io.on('disconnect')
    @authenticated_only
    def handle_disconnect():
        current_app.socket_map.delete(current_user.username)

    @socket_io.on('request new partner')
    @authenticated_only
    def handle_request_new_partner(data):
        """
        related events
            callback event: ret:request new partner
            client emit event: new partner request
        :param data: {'to_id': '...'}
        """
        to_id = data.get('to_id')
        if not to_id:
            return emit('ret:request new partner',
                        render_json(message='please tell me whom you want to request', status=400))
        to_user = User.get_user_by_id(to_id)
        if to_user is None:
            return emit('ret:request new partner',
                        render_json(message='user with id:' + to_id + ' does not exist!', status=404))

        PartnerRequest(from_id=current_user.id, to_id=ObjectId(to_id)).save()
        emit('ret:request new partner', render_json(message='request successfully', status=200))

        room_name = current_app.socket_map.get(to_user.username)
        if room_name:
            emit('new partner request', {
                'from_id': str(current_user.id)
            }, room=room_name)

    @socket_io.on('add partner')
    @authenticated_only
    def handle_add_partner(data):
        """
        related events
            callback event: ret:add partner
            client emit event: partner add
        :param data: {'from_id': '...'}
        """
        from_id = data.get('from_id')
        if not from_id:
            return emit('ret:add partner',
                        render_json(message='please tell me whom you want to add', status=400))
        from_user = User.get_user_by_id(from_id)
        if from_user is None:
            return emit('ret:add partner',
                        render_json(message='user with id:' + from_id + ' does not exist!', status=404))

        add_request = PartnerRequest.objects(from_id=ObjectId(from_id), to_id=current_user.id).first()
        if add_request is None:
            return emit('ret:add partner',
                        render_json(message='partner request does not exist', status=404))
        add_request.status = 'added'
        add_request.save()
        from_user.add_partner(current_user.id)
        current_user.add_partner(from_id)
        Chat(name=from_user.username + ', ' + current_user.username,
             members=[from_user.id, current_user.id]).save()

        emit('ret:add partner', render_json(message='add successfully', status=200))

        room_name = current_app.socket_map.get(from_user.username)
        if room_name:
            emit('partner add', {
                'to_id': str(current_user.id)
            }, room=room_name)

    @socket_io.on('reject partner')
    @authenticated_only
    def handle_reject_partner(data):
        """
        related events
            callback event: ret:reject partner
            client emit event: partner reject
        :param data: {'from_id': '...'}
        """
        from_id = data.get('from_id')
        if not from_id:
            return emit('ret:reject partner',
                        render_json(message='please tell me whom you want to reject', status=400))
        from_user = User.get_user_by_id(from_id)
        if from_user is None:
            return emit('ret:reject partner',
                        render_json(message='user with id:' + from_id + ' does not exist!', status=404))

        add_request = PartnerRequest.objects(from_id=ObjectId(from_id), to_id=current_user.id).first()
        if add_request is None:
            return emit('ret:reject partner',
                        render_json(message='partner request does not exist', status=404))
        add_request.status = 'rejected'
        add_request.save()

        emit('ret:reject partner', render_json(message='reject successfully', status=200))

        room_name = current_app.socket_map.get(from_user.username)
        if room_name:
            emit('partner reject', {
                'to_id': str(current_user.id)
            }, room=room_name)

    @socket_io.on('browse requests')
    @authenticated_only
    def handle_browse_requests():
        """
        related events
            callback event: ret:browse requests
        """
        request_list = PartnerRequest.objects(to_id=current_user.id)
        ret = []
        for req in request_list:
            temp = {
                'from_user': User.get_other_profile(user_id=req.from_id),
                'timestamp': datetime_to_timestamp(req.timestamp),
                'status': req.status
            }
            ret.append(temp)
        emit('ret:browse requests', ret)

    @socket_io.on('browse partners')
    @authenticated_only
    def handle_browse_partners():
        """
        related events
            callback event: ret:browse partners
        """
        partners_list = [User.get_other_profile(user_id=partner) for partner in current_user.partners]
        emit('ret:browse partners', partners_list)

    @socket_io.on('browse chats')
    @authenticated_only
    def handle_browse_chats():
        """
        related events
            callback event: ret:browse chats
        """
        chats_list = Chat.objects(members__in=current_user.id).order_by('-last_updated')
        ret = []
        for chat in chats_list:
            temp = {
                "id": str(chat.id),
                "name": chat.name,
                "members": [User.get_other_simplified_profile(member_id) for member_id in chat.members]
            }
            ret.append(temp)
        emit('ret:browse chats', ret)
