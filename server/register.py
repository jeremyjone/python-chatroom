'''
@Author:jeremyjone
date:2018-5-5

Register handler.
'''
import struct
from . import memory, common_handler


def register_handler(c, msg):
    uname = msg[1].decode()
    upswd = msg[2].decode()
    nkname = msg[3].decode()
    res = memory.db.register(uname, upswd, nkname)
    if res == 'OK':
        c.send(struct.pack("!L", common_handler.MessageType.register_successful))
        return
    elif res == "NAMEEXIST":
        c.send(struct.pack("!L", common_handler.MessageType.username_taken))
    else:
        c.send(struct.pack("!L", common_handler.MessageType.general_failure))
    c.close()
    memory.online_user.pop(c)
