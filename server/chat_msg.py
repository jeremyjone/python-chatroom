import struct

from . import memory, server_socket, common_handler


def userchat_handler(msg):
    send_time = msg[1].decode()
    target_user = msg[2].decode()
    from_user = msg[3]
    message = msg[4].decode()
    _online_flag = 1
    for _u in memory.online_user:
        if memory.online_user[_u][0] == target_user:
            # user online
            _online_flag = 0
            _time = send_time.encode()
            _message = message.encode()
            serializeMessage = common_handler.pack_message(
                common_handler.MessageType.on_new_message, from_user, _time, _message)
            _u.send(serializeMessage)
            # _u.send(b"hello")
            break

    # Save message to database.
    from_user = from_user.decode()
    memory.db.save_msg(from_user, target_user, _online_flag, 1, message)


def unread_msg_handler(c, user):
    res = memory.db.get_unread_msg(user)
    if not res:
        return
    for r in res:
        uid = r[0]
        utime = r[1]
        utype = r[2]
        umsg = r[3].encode()

        uname = memory.db.get_username_by_id(uid)[0].encode()
        time = ("%s年%s月%s日 %s时%s分%s秒" % (
            utime.year, utime.month, utime.day,
            utime.hour, utime.minute, utime.second)).encode()

        if utype == 1:
            # Normal msg.
            serializeMessage = common_handler.pack_message(
                common_handler.MessageType.on_new_message, uname, time, umsg)
            c.send(serializeMessage)

        elif utype == 2:
            # Broadcast.
            pass
        elif utype == 3:
            # Add friend request.
            request_user = uname
            serializeMessage = common_handler.pack_message(
                common_handler.MessageType.add_friend_request, request_user)
            c.send(serializeMessage)
        elif utype == 4:
            # Chatroom msg.
            pass


def chatroom_handler(s, msg):
    send_time = msg[1]
    chatroom_name = msg[2].decode()
    from_user = msg[3]
    message = msg[4]
    users = memory.db.get_chatroom_user(chatroom_name)
    user_list = []
    for user in users:
        us = user.split(":")
        user_list.append(us[0])

    chatroom_name = chatroom_name.encode()
    for c in memory.online_user:
        for target_user in user_list:
            if memory.online_user[c][0] == target_user:
                serializeMessage = common_handler.pack_message(
                    common_handler.MessageType.chatroom_msg, send_time, chatroom_name, from_user, message)
                c.send(serializeMessage)


def broadcast_handler(s, msg):
    pass
