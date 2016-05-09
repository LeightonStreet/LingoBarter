import functools

from datetime import datetime

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
        # parse data
        to_chat = ObjectId(data.get('to_chat'))
        page_id = int(data.get('page_id'))
        page_size = int(data.get('page_size'))

        # handle bad requests
        if not to_chat:
            return emit('ret:browse messages',
                        render_json(message='please tell me which chat you want to browse', status=400))
        if not page_id:
            return emit('ret:browse messages',
                        render_json(message='please tell me page id', status=400))
        if not page_size:
            return emit('ret:browse messages',
                        render_json(message='please tell me page size', status=400))

        # if this chat does not exist
        if Chat.objects(id=to_chat).first() is None:
            return emit('ret:browse messages',
                        render_json(message='chat with id:' + str(to_chat) + ' does not exist!', status=404))

        # get all messages whose to_chat equals to to_chat
        start_record_num = page_id * page_size
        end_record_num = start_record_num + page_size
        # todo: do we need to sort messages
        messages_list = Message.objects(to_chat=to_chat).order_by('-timestamp')[start_record_num: end_record_num]
        ret = []
        for message in messages_list:
            temp = {
                'from_id': str(message.from_id),
                'to_chat': str(message.to_chat),
                'type': message.type,
                'voice_file_path': message.voice_file_path if message.voice_file_path is not None else None,
                'text_content': message.text_content if message.text_content is not None else None,
                'image_file_path': message.image_file_path if message.image_file_path is not None else None,
                'timestamp': dateformat.datetime_to_timestamp(message.timestamp) if message.timestamp is not None else None
            }
            ret.append(temp)
        emit('ret:browse messages', ret)

    @socket_io.on('fetch undelivered messages')
    @authenticated_only
    def handle_fetch_undelivered_messages():
        """
        related events
            callback event: ret:fetch undelivered messages
        """
        current_user = get_current_user()
        chats_list = Chat.objects(members=current_user.id)
        ret = {} # store result

        for chat in chats_list:
            messages_list = Message.objects(to_chat=chat.id).order_by('-timestamp')  # get all related messages
            messages_of_one_chat = []  # store messages that have not been delivered to current user in one chat
            for message in messages_list:
                if current_user.id in message.undelivered:  # if this message has not been delivered to current user
                    temp_message = {
                        'from_id': str(message.from_id),
                        'to_chat': str(message.to_chat),
                        'type': message.type,
                        'voice_file_path': message.voice_file_path if message.voice_file_path is not None else None,
                        'text_content': message.text_content if message.text_content is not None else None,
                        'image_file_path': message.image_file_path if message.image_file_path is not None else None,
                        'timestamp': dateformat.datetime_to_timestamp(message.timestamp) if message.timestamp is not None else None
                    }
                    messages_of_one_chat.append(temp_message)  # fetch message
            if messages_of_one_chat:  # if there is any undelivered message in this chat
                ret[str(chat.to_chat)] = messages_of_one_chat  # fetch this chat

        emit('ret:fetch undelivered messages', ret)

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

    @socket_io.on('create group chat')
    @authenticated_only
    def handle_create_group_chat(data):
        """
        related events
            callback event: ret:create group chat
            :param data: {"members_id_list": [user_id]}
                         (user non-inclusive, if len(list)<=1, revert)
            client emit event: group chat create
                                (user who create this group chat inclusive)
        """
        members_id_list = [ObjectId(member_id) for member_id in data.get('members_id_list')]
        current_user = get_current_user()
        members_list = []  # new members
        member_does_not_exist = False
        member_is_not_partner = False
        chat_name = current_user.username  # name of this group chat

        # if there are less than two elements in members_id_list, reject
        # not a group chat
        if len(members_id_list) <= 1:
            return emit('ret:create group chat',
                        render_json(
                            message='please give me more user id. Cannot create a group chat with only two users',
                            status=400))

        # get all members, if one or more of them do not exist, error
        # if one or more of them are not partner of current user, error
        member_num = 0
        for member_id in members_id_list:
            if member_id == current_user.id:
                continue
            member = User.objects(id=member_id).first()
            if member is None:
                member_does_not_exist = True
                break
            if member not in current_user.partners:
                member_is_not_partner = True
                break
            members_list.append(member)
            member_num = member_num + 1
            chat_name = chat_name + ', ' + member.username

        if member_num <= 1:
            return emit('ret:create group chat',
                        render_json(
                            message='please give me more user id. Cannot create a group chat with only two users',
                            status=400))

        if member_does_not_exist:
            return emit('ret:create group chat',
                        render_json(
                            message='please give me correct user id. User you want to add to this chat does not exist',
                            status=400))

        if member_is_not_partner:
            return emit('ret:create group chat',
                        render_json(
                            message='please give me correct user id. User you want to add to this chat is not your partner',
                            status=400))

        # create a group chat
        group_chat = Chat(name=chat_name, members=members_id_list)
        group_chat.save()

        # notify front-end that this operation succeed
        emit('ret:create group chat', render_json(message='create group chat successfully', status=200))

        # notify all members of this group chat that they have been invited
        for member_id in members_id_list:
            room_name = current_app.socket_map.get(member_id)
            if room_name:
                notification = {
                    "id": str(group_chat.id),
                    "name": group_chat.name,
                    "members": [User.get_other_simplified_profile(user_id=member_id) for member_id in group_chat.members]
                }
                emit('group chat create', notification)

    @socket_io.on('add member to group chat')
    @authenticated_only
    def handle_add_member_to_group_chat(data):
        """
        related events
            callback event: ret:add member to group chat
            :param data: {"members_id_list": [user_id], "to_chat": ...}
                         (user non-inclusive, if len(list)<=0, revert)
            client emit event: group chat update
                                (user who update this group chat inclusive)
        """
        members_id_list = [ObjectId(member_id) for member_id in data.get('members_id_list')]
        to_chat = ObjectId(data.get('to_chat'))
        current_user = get_current_user()
        members_list = []
        member_does_not_exist = False
        member_is_not_partner = False
        chat_name = ", "  # update information for name of this group chat
        group_chat = Chat.objects(id=to_chat).first()

        # if this chat does not exist, error
        if group_chat is None:
            return emit('ret:add member to group chat',
                        render_json(
                            message='please give me correct to_chat',
                            status=400))

        # if there are less than two elements in members_id_list, reject
        # not a group chat
        if len(members_id_list) <= 0:
            return emit('ret:add member to group chat',
                        render_json(
                            message='please give me more user id. Cannot add zero new member to group chat',
                            status=400))

        # get all members, if one or more of them do not exist, error
        # if one or more of them are not partner of current user, error
        member_num = 0
        for member_id in members_id_list:
            if member_id == current_user.id:
                continue
            member = User.objects(id=member_id).first()
            if member is None:
                member_does_not_exist = True
                break
            if member_id not in current_user.partners:
                member_is_not_partner = True
                break
            members_list.append(member)
            member_num = member_num + 1
            chat_name = chat_name + member.username + ', '
        chat_name = chat_name[:-2]  # remove last ", "

        if member_num <= 0:
            return emit('ret:add member to group chat',
                        render_json(
                            message='please give me more user id. Cannot add zero new member to group chat',
                            status=400))

        if member_does_not_exist:
            return emit('ret:add member to group chat',
                        render_json(
                            message='please give me correct user id. User you want to add to this chat does not exist',
                            status=400))

        if member_is_not_partner:
            return emit('ret:add member to group chat',
                        render_json(
                            message='please give me correct user id. User you want to add to this chat is not your partner',
                            status=400))

        # update group chat
        group_chat.last_updated = datetime.now()
        group_chat.name = group_chat.name + chat_name
        group_chat.members = group_chat.members + members_id_list
        group_chat.save()

        # notify front-end that this operation succeed
        emit('ret:add member to group chat', render_json(message='add new member to group chat successfully',
                                                         status=200))

        # notify all members of this group chat that they have been invited
        for member_id in group_chat.members:
            room_name = current_app.socket_map.get(member_id)
            if room_name:
                notification = {
                    "id": str(group_chat.id),
                    "name": group_chat.name,
                    "members": [User.get_other_simplified_profile(user_id=member_id) for member_id in group_chat.members]
                }
                emit('group chat update', notification)

    @socket_io.on('remove member from group chat')
    @authenticated_only
    def handle_remove_member_from_group_chat(data):
        """
        related events
            callback event: ret:remove member to group chat
            :param data: {"members_id_list": [user_id], "to_chat": ...}
                         (user non-inclusive, if len(list)<=0, revert)
            client emit event: group chat update
                                (user who update this group chat inclusive)
        """
        members_id_list = [ObjectId(member_id) for member_id in data.get('members_id_list')] # members to delete
        to_chat = ObjectId(data.get('to_chat'))
        current_user = get_current_user()
        member_not_in_group_chat = False
        member_does_not_exist = False
        group_chat = Chat.objects(id=to_chat).first()

        # if this chat does not exist, error
        if group_chat is None:
            return emit('ret:remove member to group chat',
                        render_json(
                            message='please give me correct to_chat',
                            status=400))

        if current_user.id != group_chat.members[0].id:
            return emit('ret:remove member to group chat',
                        render_json(
                            message='current user is not allowed to delete this group chat',
                            status=403))

        # if there are less than two elements in members_id_list, reject
        # not a group chat
        if len(members_id_list) <= 0:
            return emit('ret:remove member to group chat',
                        render_json(
                            message='please give me more user id. Cannot remove zero member from group chat',
                            status=400))

        # get all members, if one or more of them are do not exist, error
        # if one or more of them are not in this group chat, error
        member_num = 0
        for member_id in members_id_list:
            if member_id == current_user.id:
                continue
            member = User.objects(id=member_id).first()
            if member is None:
                member_does_not_exist = True
                break
            if member_id not in group_chat.members:
                member_not_in_group_chat = True
                break
            member_num = member_num + 1

        if member_num <= 0:
            return emit('ret:remove member to group chat',
                        render_json(
                            message='please give me more user id. Cannot remove zero member from group chat',
                            status=400))

        if member_does_not_exist:
            return emit('ret:remove member to group chat',
                        render_json(
                            message='please give me correct user id. User you want to remove from this chat does not exist',
                            status=400))

        if member_not_in_group_chat:
            return emit('ret:remove member to group chat',
                        render_json(
                            message='please give me correct user id. User you want to remove from this chat is not in this group chat',
                            status=400))

        # update group chat

        # remove members
        for member_id in members_id_list:
            group_chat.members.remove(member_id)

        # update name of group chat
        chat_name = ""
        for member_id in group_chat.members:
            member = User.objects(id=member_id).first()
            chat_name = chat_name + member.username + ', '
        chat_name = chat_name[:-2]  # remove ", " at the end of chat_name
        group_chat.name = chat_name

        group_chat.last_updated = datetime.now()
        group_chat.save()

        # notify front-end that this operation succeed
        emit('ret:remove member from group chat', render_json(message='remove member from group chat successfully',
                                                              status=200))

        # notify all members of this group chat that they have been invited
        for member_id in group_chat.members:
            room_name = current_app.socket_map.get(member_id)
            if room_name:
                notification = {
                    "id": str(group_chat.id),
                    "name": group_chat.name,
                    "members": [User.get_other_simplified_profile(user_id=member_id) for member_id in group_chat.members]
                }
                emit('group chat update', notification)

