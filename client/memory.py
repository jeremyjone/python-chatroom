'''
@Author:jeremyjone
date:2018-5-4

Keep general information for client.
'''
IP = "0.0.0.0"
PORT = "5555"

sc = None

Login_window = None

Contact_window = []

# {username: window}
Chat_window = {}

# {username: [(time, from_user, message1, flag), (time, from_user, message2, flag), ...]}
recv_message = {}

# {(1, friend_username): friend_nickname}
# {(2, chatroom_name): chatroom_show_name(群  chatroom_name)}
friend_list = {}

# {chatroom_name: [(username1, nickname1), (username2, nickname2), ...]}
chatroom_user_list = {}

recv_msg_thread = None

# {"username": "nickname"} 
current_user = {}
username = ""
sc = None
tk_root = None
