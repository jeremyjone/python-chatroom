'''
@Author:jeremyjone
Date:2018-5-5

This module contains socket information, allowing the
server to monitor the information sent by the client,
and to handle and distribute the requests, and return
the corresponding data to the client.
'''
from socket import *
from threading import *
import os
import struct

from . import memory, login, chat_msg, manage_friend,\
    manage_group, register, common_handler


def server(IP, PORT):
    '''
    Create socket by TCP.
    '''
    sk = socket(AF_INET, SOCK_STREAM)
    sk.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sk.bind((IP, int(PORT)))
    sk.listen(5)
    memory.server_socket = sk
    return sk


def distribute_handler(s, ad):
    '''
    Receive data and distribute them to different modules
    for processing respectively.
    '''
    while True:
        try:
            data = s.recv(4096)
            msg = common_handler.unpack_message(data)
            # Recv large file
            if msg[0] == common_handler.MessageType.large_file:
                msg_buffer += msg[1]
                if msg[2] == 0:
                    msg = msg_buffer
                    msg_buffer = None
                else:
                    continue

            if msg[0] == common_handler.MessageType.register:
                # Register
                print("接收到注册请求")
                register.register_handler(s, msg)

            elif msg[0] == common_handler.MessageType.login:
                # Login
                print("接收到登录请求")
                login.login_handler(s, ad, msg)

            elif msg[0] == common_handler.MessageType.add_friend:
                # Add friend
                print("接收到添加好友请求")
                manage_friend.add_friend_handler(s, msg)

            elif msg[0] == common_handler.MessageType.confirm_friend_request:
                # confirm add friend
                print("接收到确认添加好友请求")
                manage_friend.confirm_handler(s, msg)

            elif msg[0] == common_handler.MessageType.delete_friend:
                # delete friend
                print("接收到删除好友请求")
                manage_friend.del_friend_handler(s, msg)

            elif msg[0] == common_handler.MessageType.query_friend:
                # Get friend infomation
                print("接收到获取好友列表请求")
                manage_friend.get_friend_handler(s)

            elif msg[0] == common_handler.MessageType.send_message:
                # Chat message
                print("接收到发送消息请求")
                chat_msg.userchat_handler(msg)

            elif msg[0] == common_handler.MessageType.chatroom_message:
                # Chatroom message
                print("接收到聊天室信息请求")
                chat_msg.chatroom_handler(s, msg)

            elif msg[0] == common_handler.MessageType.broadcast:
                # Broadcast message
                print("接收到广播请求")
                chat_msg.broadcast_handler(s, msg)

            elif msg[0] == common_handler.MessageType.create_room:
                # Create chatroom
                print("接收到创建群聊请求")
                manage_group.chatroom_handler(s, msg)

            elif msg[0] == common_handler.MessageType.join_room:
                # User join/leave chatroom
                print("接收到加入/退出群聊请求")
                manage_group.user_join_leave_handler(s, msg, "join")

            elif msg[0] == common_handler.MessageType.leave_room:
                # User join/leave chatroom
                print("接收到加入/退出群聊请求")
                manage_group.user_join_leave_handler(s, msg, "leave")

            elif msg[0] == common_handler.MessageType.logout:
                # User logout
                print("接收到用户登出信号")
                login.logout_handler(s)

            elif msg[0] == common_handler.MessageType.query_room_users:
                print("收到用户请求刷新聊天室列表")
                manage_group.query_chatroom_user(s, msg)

        except struct.error:
            pass
        except ConnectionResetError as e:
            print(e)
            del memory.online_user[s]
            memory.window.add_user_list()
        except OSError as e:
            pass
        # except Exception as e:
        #     print("服务器接收信息时遇到一个未知问题 >>", e)


def server_handler(sk):
    '''
    Loop monitor, receive data, simple handler and distribute
    data to different modules for further processing.
    '''
    print("Server is running...")
    while True:
        try:
            c, ad = sk.accept()
            print(ad)
        except KeyboardInterrupt:
            os._exit(0)
        except Exception:
            continue

        t1 = Thread(target=distribute_handler, args=(c, ad,))
        t1.start()


def run(IP, PORT):
    s = server(IP, PORT)
    server_handler(s)


if __name__ == "__main__":
    run()
