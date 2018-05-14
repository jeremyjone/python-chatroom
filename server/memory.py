'''
@Author:jeremyjone
date:2018-5-4

Keep general information for server.
'''
from .DB_Handler import DB_Handler


# {connect: (username, IP, PORT)}
online_user = {}

server_socket = None

server_socket_listener = None

db = DB_Handler()

window = None
