'''
@Author:jeremyjone
date:2018-5-5

Login handler.
'''
from . import memory, common_handler


def login_handler(c, ad, msg):
    uname = msg[1].decode()
    upswd = msg[2].decode()

    res = memory.db.login_check(uname, upswd)

    if res == 'OK':
        nickname = memory.db.get_user_nickname(uname)[0].encode()
        serializeMessage = common_handler.pack_message(common_handler.MessageType.login_successful, nickname)
        c.send(serializeMessage)
        memory.online_user[c] = (uname, ad[0], ad[1])
        memory.window.add_user_list()
    else:
        result = b"login fail"
        serializeMessage = common_handler.pack_message(common_handler.MessageType.login_failed, result)
        c.send(serializeMessage)
        c.close()
        # memory.online_user.pop(c)


def logout_handler(c):
    del memory.online_user[c]
    memory.window.add_user_list()
