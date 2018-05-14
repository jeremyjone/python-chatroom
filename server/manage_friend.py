'''
title: Manage_Friend method.
@Author: jeremyjone
date: 2018-5-6

Supply to add friend & confirm add, delete friend, read friends
list, convenient user management friend relationship.
'''
import struct
from .memory import *

from . import common_handler, chat_msg, memory


def add_friend_handler(c, msg):
    add_name = msg[1].decode()
    res = db.user_exist(add_name)
    if not res:
        serializeMessage = common_handler.pack_message(common_handler.MessageType.user_not_exist, b'no_user')
        c.send(serializeMessage)
    else:
        for i in online_user:
            if online_user[i][0] == res[0]:
                # online
                request_user = online_user[c][0].encode()
                serializeMessage = common_handler.pack_message(common_handler.MessageType.add_friend_request, request_user)
                i.send(serializeMessage)
                return
        # If user offline, save msg into database.
        db.save_msg(online_user[c][0], add_name, 1, 3, "add friend")


def confirm_handler(c, msg):
    result = msg[1].decode()
    respoonse_user = msg[2].decode()
    request_user = msg[3].decode()
    for i in online_user:
        if online_user[i][0] == request_user:
            request_socket = i
            serializeMessage = common_handler.pack_message(common_handler.MessageType.add_friend_result, result.encode(), respoonse_user.encode())
            i.send(serializeMessage)
            break
    if result == "OK":
        # Add to database.
        res = db.user_add_friend(request_user, respoonse_user)
        try:
            if res == "NG":
                raise ValueError("添加好友产生了一个未知错误，没有添加成功，\
                    好友关系人>> {}  和  {}".format(request_user, online_user[request_socket][0]))
            else:
                get_friend_handler(request_socket)
                get_friend_handler(c)
        except ValueError as e:
            print(e)


def del_friend_handler(c, msg):
    target_user = msg[1].decode()
    request_user = msg[2].decode()
    res = memory.db.user_del_friend(request_user, target_user)
    if res == "OK":
        get_friend_handler(c)
        for i in online_user:
            if online_user[i][0] == target_user:
                get_friend_handler(i)
    else:
        _msg = b"delete failed"
        serializeMessage = common_handler.pack_message(common_handler.MessageType.delete_friend_failed, _msg)
        c.send(serializeMessage)


def get_friend_handler(c):
    username = online_user[c][0]
    res_user = db.user_friend(username)
    if res_user == "NF":
        friend = "no friend"
    else:
        # Return friends list
        friend = " + ".join(res_user)

    res_room = db.query_chatroom(username)
    if res_room == "NF":
        chatroom = 'no chatroom'
    else:
        chatroom = " + ".join(res_room)

    total_friend = friend.encode()
    total_chatroom = chatroom.encode()
    serializeMessage = common_handler.pack_message(common_handler.MessageType.query_friend_list, total_friend, total_chatroom)
    c.send(serializeMessage)
    chat_msg.unread_msg_handler(c, username)
