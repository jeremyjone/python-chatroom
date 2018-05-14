'''
@Author:jeremyjone
Date:2018-5-7

This is common handler module

Socket send and recive data Module:
    struct.pack two layers,
        first layer pack message and data.
        second layer pack some necessary message incule
        MessageType, MessageLength, messageself/dataself.
    struct.unpack three layers,
        first layer unpack_from by fmt("LLL"), get a tuple
        include MessageType, MessageLength.
        second layer unpack and get the received message.
        third layer unpack can get messageself/dataself.

Secure encryption Module:
    a cryptographic operation for a password.
'''
import struct
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex


class prpcrypt():

    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_CBC

    def encrypt(self, text):
        '''
        Encrypt emthod.

        The encrypt key must be 16(AES-128) / 24(AES-192) / 32(AES-256) bytes.
        If text not the multiplier of 16, must be complemented.
        After encrypt, change to Hexadecimal.
        '''
        cryptor = AES.new(self.key, self.mode, self.key)
        # text = text.encode("utf-8")
        length = 16
        count = len(text)
        add = length - (count % length)
        text = text + (b'\0' * add)
        self.ciphertext = cryptor.encrypt(text)
        return b2a_hex(self.ciphertext)

    def decrypt(self, text):
        '''
        Decrypt method.
        After decrypt, use strip() cut blanks.
        '''
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = cryptor.decrypt(a2b_hex(text))
        return plain_text.rstrip(b'\0')


def pack_message(MessageType, *args):
    fmt = ''
    for i in args:
        if type(i) == int:
            fmt += "L"
        elif type(i) == bytes:
            fmt += str(len(i)) + "s"
        elif type(i) == float:
            fmt += "f"
    print("fmt>>", fmt)
    serializeMessage = struct.pack(fmt, *args)
    fmt = fmt.encode()
    fmt_send = "!LLL" + str(len(fmt)) + "s" + str(len(serializeMessage)) + "s"
    serializeData = struct.pack(fmt_send, MessageType, len(fmt),
                                len(serializeMessage), fmt, serializeMessage)
    pack_to_send = prpcrypt("jeremyjonejeremy").encrypt(serializeData)
    return pack_to_send


def unpack_message(data):
    serializeMessage = prpcrypt("jeremyjonejeremy").decrypt(data)
    if struct.unpack_from("!L", serializeMessage)[0] > 200:
        # 表示坏球了
        return struct.unpack_from("!L", serializeMessage)

    fmt = "!LLL"
    # layer1
    _t = struct.unpack_from(fmt, serializeMessage)
    # MessageType
    get_message = [_t[0]]
    fmt += str(_t[1]) + "s" + str(_t[2]) + "s"
    # layer2
    _msg = struct.unpack(fmt, serializeMessage)
    # layer3
    res = struct.unpack(_msg[3].decode(), _msg[4])
    for i in res:
        # get a list ---> [MessageType, data1, data2 ...]
        get_message.append(i)
    return get_message


class MessageType:
    # === Client Action 1-100
    # username, password
    login = 1
    # username, passowrd, nickname
    register = 2
    friend_list = 3
    add_friend = 4
    confirm_friend_request = 5
    delete_friend = 6
    query_friend = 7

    send_message = 11
    chatroom_message = 12

    join_room = 21
    create_room = 22
    query_room_users = 23
    leave_room = 24
    bad = 44

    logout = 88

    # === Server Action 101-200
    login_successful = 100
    register_successful = 101
    contact_info = 103
    chat_history = 104
    query_friend_list = 105
    add_friend_request = 106
    add_friend_result = 107
    friend_on_off_line = 108

    large_file = 111

    create_room_res = 114
    query_room_users_result = 115
    room_user_on_off_line = 116

    on_new_message = 121
    chatroom_msg = 122
    incoming_friend_request = 123
    join_leave_chatroom = 124

    delete_friend_failed = 141

    broadcast = 198
    broadcast_to_client = 199

    # === Failure 201-300
    login_failed = 201
    username_taken = 202
    general_failure = 203
    general_msg = 204
    user_not_exist = 205
