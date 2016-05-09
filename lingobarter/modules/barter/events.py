import functools

from bson.objectid import ObjectId
from flask import current_app, request
from flask.ext.security.decorators import _check_token
from flask_socketio import disconnect
from flask_socketio import emit
from lingobarter.core.json import render_json
from lingobarter.modules.accounts.models import User
from lingobarter.utils import get_current_user, dateformat
from .models import PartnerRequest, Chat, Message


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
        current_user = get_current_user()
        current_app.socket_map.add(current_user.id, request.sid)
        emit('connected', render_json(message='connected', status=200))

    @socket_io.on('disconnect')
    @authenticated_only
    def handle_disconnect():
        current_user = get_current_user()
        current_app.socket_map.delete(current_user.id)

    @socket_io.on('request new partner')
    @authenticated_only
    def handle_request_new_partner(data):
        """
        related events
            callback event: ret:request new partner
            client emit event: new partner request
        :param data: {'to_id': '...'}
        """
        current_user = get_current_user()
        to_id = data.get('to_id')

        if to_id == str(current_user.id):
            return emit('ret:request new partner',
                        render_json(message='You cannot add yourself', status=403))

        if not to_id:
            return emit('ret:request new partner',
                        render_json(message='please tell me whom you want to request', status=400))

        if current_user.has_partner(to_id):
            return emit('ret:request new partner',
                        render_json(message='This user is already your partner', status=409))

        to_user = User.get_user_by_id(to_id)
        if to_user is None:
            return emit('ret:request new partner',
                        render_json(message='user with id:' + to_id + ' does not exist!', status=404))

        if PartnerRequest.objects(from_id=current_user.id, to_id=ObjectId(to_id), status="pending").first():
            return emit('ret:request new partner',
                        render_json(message='Same pending request exist! Please wait for other user', status=403))

        PartnerRequest(from_id=current_user.id, to_id=ObjectId(to_id)).save()
        emit('ret:request new partner', render_json(message='request successfully', status=200))

        room_name = current_app.socket_map.get(to_id)
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
        current_user = get_current_user()
        from_id = data.get('from_id')
        if not from_id:
            return emit('ret:add partner',
                        render_json(message='please tell me whom you want to add', status=400))
        from_user = User.get_user_by_id(from_id)
        if from_user is None:
            return emit('ret:add partner',
                        render_json(message='user with id:' + from_id + ' does not exist!', status=404))

        add_request = PartnerRequest.objects(from_id=ObjectId(from_id), to_id=current_user.id, status="pending").first()
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

        room_name = current_app.socket_map.get(from_id)
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
        current_user = get_current_user()
        from_id = data.get('from_id')
        if not from_id:
            return emit('ret:reject partner',
                        render_json(message='please tell me whom you want to reject', status=400))
        from_user = User.get_user_by_id(from_id)
        if from_user is None:
            return emit('ret:reject partner',
                        render_json(message='user with id:' + from_id + ' does not exist!', status=404))

        add_request = PartnerRequest.objects(from_id=ObjectId(from_id), to_id=current_user.id, status="pending").first()
        if add_request is None:
            return emit('ret:reject partner',
                        render_json(message='partner request does not exist', status=404))

        add_request.status = 'rejected'
        add_request.save()

        emit('ret:reject partner', render_json(message='reject successfully', status=200))

        room_name = current_app.socket_map.get(from_id)
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
        current_user = get_current_user()
        request_list = PartnerRequest.objects(to_id=current_user.id)
        ret = []
        for req in request_list:
            temp = {
                'from_user': User.get_other_profile(user_id=req.from_id),
                'timestamp': dateformat.datetime_to_timestamp(req.timestamp),
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
        current_user = get_current_user()
        partners_list = [User.get_other_profile(user_id=partner) for partner in current_user.partners]
        emit('ret:browse partners', partners_list)

    @socket_io.on('browse chats')
    @authenticated_only
    def handle_browse_chats():
        """
        related events
            callback event: ret:browse chats
        """
        current_user = get_current_user()
        chats_list = Chat.objects(members=current_user.id).order_by('-last_updated')
        ret = []
        for chat in chats_list:
            temp = {
                "id": str(chat.id),
                "name": chat.name,
                "members": [User.get_other_simplified_profile(user_id=member_id) for member_id in chat.members]
            }
            ret.append(temp)
        emit('ret:browse chats', ret)

    @socket_io.on('browse messages')
    @authenticated_only
    def handle_browse_messages(data):
        """
        related events
            callback event: ret:browse messages
        :param data: {"to_chat": ..., "page_id": ..., "page_size": ...}
        """
        pass

    @socket_io.on('fetch undelivered messages')
    @authenticated_only
    def handle_fetch_undelivered_messages():
        """
        related events
            callback event: ret:fetch undelivered messages
        """
        pass

    @socket_io.on('send message')
    @authenticated_only
    def handle_send_message(data):
        """
        related events
            callback event: ret:send message
            :param data: {"to_chat": ..., "type": ..., "payload": "voice_stream|text_content|image_stream": ...}
        """
        if data.get("to_chat") is None or data.get("type") is None or data.get("payload") is None:
            return emit('ret:send message', render_json(message="Message is not complete", status=400))

        current_user = get_current_user()
        current_chat = Chat.get_chat_by_id(data['to_chat'])

        if current_user.id not in current_chat.members:
            return emit('ret:send message', render_json(message="You do not belong to this chat", status=403))

        online_set = set([ObjectId(user) for user in current_app.socket_map.get_all_users()])
        member_set = set(current_chat.members)
        offline_set = member_set - online_set

        message = Message(from_id=current_user.id, to_chat=ObjectId(data['to_chat']))
        message.undelivered = list(offline_set)
        if data['type'] == 'text':
            message.type = 'text'
            message.text_content = data['payload']

            ret_payload = data['payload']
        elif data['type'] == 'voice':
            ret_payload = '...'
            pass
        elif data['type'] == 'image':
            ret_payload = '...'
            pass
        else:
            return emit('ret:send message', render_json(message="Unknown message type", status=400))

        current_chat.last_updated = message.timestamp
        current_chat.save()
        message.save()

        ret_message = {
            'from_id': str(current_user.id),
            'to_chat': data['to_chat'],
            'type': data['type'],
            'payload': ret_payload,
            'timestamp': dateformat.datetime_to_timestamp(message.timestamp)
        }
        for online_id in (online_set & member_set):
            emit('message send', ret_message, room=current_app.socket_map.get(online_id))

        emit('ret:send message', render_json(message="Message has been sent", status=200))

