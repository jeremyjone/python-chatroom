'''
@Author:jeremyjone
Date:2018-5-5

This module provides methods and interfaces for clients
to connect to the server.
'''
from socket import *
import time
import struct
from threading import Thread

from . import memory, contact_form, chat_form, common_handler


def send_msg(data):
    memory.sc.send(data)


def recv_msg(c):
    try:
        msg = c.recv(4096)
    except Exception:
        pass
    return msg


def connect_to_server(IP, PORT):
    s = socket(AF_INET, SOCK_STREAM)
    try:
        s.connect((IP, int(PORT)))
        return s
    except Exception:
        return "connect_fail"


def keep_recv():
    print("线程启动")
    msg_buffer = None
    while True:
        # try:
        print("开始监听")
        data = memory.sc.recv(4096)
        msg = common_handler.unpack_message(data)
        # Recv large file
        if msg[0] == common_handler.MessageType.large_file:
            msg_buffer += msg[1]
            if msg[2] == 0:
                msg = msg_buffer
                msg_buffer = None
            else:
                continue

        elif msg[0] == common_handler.MessageType.query_friend_list:
            # friend_list
            print("收到好友列表")
            contact_form.show(msg)

        elif msg[0] == common_handler.MessageType.on_new_message:
            # chatmsg
            print("接收到聊天信息")
            chat_form.chatmsg_handler(msg)

        elif msg[0] == common_handler.MessageType.chatroom_msg:
            # chatroom_msg
            print("接收到群聊信息")
            chat_form.chatroom_msg_handler(msg)

        elif msg[0] == common_handler.MessageType.create_room_res:
            print("接收到创建聊天室反馈信息")
            contact_form.chatroom_handler(msg)

        elif msg[0] == common_handler.MessageType.query_room_users_result:
            print("接收到创建聊天室反馈信息")
            chat_form.chatroom_user_update(msg)

        elif msg[0] == common_handler.MessageType.user_not_exist:
            print("接收到希望添加的好友不存在")
            contact_form.recive_some_info(msg)

        elif msg[0] == common_handler.MessageType.add_friend_request:
            print("接收到添加好友请求")
            contact_form.recive_some_info(msg)

        elif msg[0] == common_handler.MessageType.add_friend_result:
            print("接收到确认添加好友回复")
            contact_form.recive_some_info(msg)

        elif msg[0] == common_handler.MessageType.join_leave_chatroom:
            print("接收到出入聊天室")
            contact_form.recive_some_info(msg)

        elif msg[0] == common_handler.MessageType.delete_friend_failed:
            print("接收到删除好友失败")
            contact_form.recive_some_info(msg)

        # except struct.error:
        #     pass
        # except Exception as e:
        #     print(e)
    memory.sc.close()


def keep_connect_listener():
    t = Thread(target=keep_recv)
    memory.recv_msg_thread = t
    t.start()
    return
