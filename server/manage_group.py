'''
@title: manage group
@Author: jeremyjone
date: 2018-5-9

Manage all about chatroom handler.
'''
import struct

from . import memory, common_handler


def chatroom_handler(s, msg):
    chatroom_name = msg[1].decode()
    res_create = memory.db.create_chatroom(chatroom_name)
    res_join = ''
    if res_create == "EXIST":
        m = b"EXIST"
    else:
        res_join = memory.db.chatroom_user(
            chatroom_name, memory.online_user[s][0], 'join')
    cn = b''
    if res_create == res_join == "OK":
        m = b"OK"
        cn = chatroom_name.encode()
    else:
        m = b"NG"
    serializeMessage = common_handler.pack_message(common_handler.MessageType.create_room_res, m, cn)
    s.send(serializeMessage)


def user_join_leave_handler(s, msg, handler):
    chatroom_name = msg[1].decode()
    name = msg[2].decode()
    res = memory.db.chatroom_user(chatroom_name, name, handler)
    if res == "OK":
        res = b"OK"
    else:
        res = b"NG"
    serializeMessage = common_handler.pack_message(common_handler.MessageType.join_leave_chatroom, res)
    s.send(serializeMessage)


def query_chatroom_user(s, msg):
    chatroom_name = msg[1].decode()
    res = memory.db.get_chatroom_user(chatroom_name)

    if res == "NF":
        ct_user = "no more user"
    else:
        # Return friends list
        ct_user = " + ".join(res)
    total_ct_user = ct_user.encode()
    chatroom_name = chatroom_name.encode()

    serializeMessage = common_handler.pack_message(common_handler.MessageType.query_room_users_result, chatroom_name, total_ct_user)
    s.send(serializeMessage)
