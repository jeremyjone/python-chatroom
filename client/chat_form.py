'''
@title: Chat Window
@Author: jeremyjone
date: 2018-5-6

Chat widnow for user to input text and send, while receiving and
displaying messages from other people.
'''
import tkinter as tk
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter import colorchooser
from tkinter import simpledialog
import struct
import datetime as dtime

from . import client_socket, memory, common_handler


class ChatForm(tk.Frame):
    font_color = "#000000"
    font_size = 12

    def on_list_click(self, e):
        name = self.chatroom_user_list.get(
            self.chatroom_user_list.curselection())
        for tmp in memory.chatroom_user_list[self.username]:
            if tmp[1] == name:
                uname = tmp[0]

        for fn in memory.friend_list:
            if uname == fn[1]:
                # It's friend...
                uname = memory.friend_list[fn] + "  (" + uname + ")"
                run(uname)
                return
        # Not friend...
        result = messagebox.askokcancel(
            "还不是好友？", "你和" + name + "还不是好友，是否立即添加？")
        if result:
            friend_name = uname.encode()
            serializeMessage = common_handler.pack_message(common_handler.MessageType.add_friend, friend_name)
            client_socket.send_msg(serializeMessage)
            messagebox.showinfo('添加好友', '好友请求已发送')

    def __init__(self, master=None, username=None, nickname="Unkown"):
        super().__init__(master)
        self.master = master
        self.username = username
        self.nickname = nickname
        self.master.resizable(width=True, height=True)
        self.master.geometry('660x500')
        self.master.minsize(420, 370)

        self.master.title("与 {} 聊天中...".format(self.nickname))
        memory.Chat_window[self.username] = self
        print(memory.Chat_window)

        # Chatroom window

        for v in memory.friend_list:
            if v[1] == self.username:
                if v[0] == 2:
                    self.left_frame = tk.Frame(self)

                    self.scroll = Scrollbar(self.left_frame)
                    self.scroll.pack(side=RIGHT, fill=Y)
                    self.chatroom_user_list = Listbox(
                        self.left_frame, yscrollcommand=self.scroll.set)
                    self.chatroom_user_list.bind(
                        "<Double-Button-1>", self.on_list_click)
                    self.scroll.config(command=self.chatroom_user_list.yview)
                    self.chatroom_user_list.pack(expand=True, fill=BOTH)
                    self.update_chatroom_user_list(v[1])
                    self.left_frame.pack(side=RIGHT, expand=True, fill=BOTH)

        # self.friend_name = tk.Label(
        #     self.left_frame, text=nickname, bg='#EEE', width=15)
        # self.friend_name.pack(expand=True, fill=BOTH, ipadx=5, ipady=5)

        self.right_frame = tk.Frame(self, bg='white')
        self.right_frame.pack(side=LEFT, expand=True, fill=BOTH)
        self.input_frame = tk.Frame(self.right_frame)
        self.input_textbox = ScrolledText(self.right_frame, height=7)
        self.input_textbox.bind("<Control-Return>", self.send_message)
        self.input_textbox.bind_all('<Key>', self.apply_font_change)

        self.send_btn = tk.Button(self.input_frame, text='发送消息(Ctrl+Enter)',
                                  command=self.send_message)
        self.send_btn.pack(side=RIGHT, expand=False)

        self.font_btn = tk.Button(
            self.input_frame, text='字体颜色', command=self.choose_color)
        self.font_btn.pack(side=LEFT, expand=False)

        self.font_btn = tk.Button(
            self.input_frame, text='字体大小', command=self.choose_font_size)
        self.font_btn.pack(side=LEFT, expand=False)

        # self.image_btn = tk.Button(
        #     self.input_frame, text='发送图片', command=self.send_image)
        # self.image_btn.pack(side=LEFT, expand=False)

        self.chat_box = ScrolledText(self.right_frame, bg='white')
        self.input_frame.pack(side=BOTTOM, fill=X, expand=False)
        self.input_textbox.pack(side=BOTTOM, fill=X,
                                expand=False, padx=(0, 0), pady=(0, 0))
        self.chat_box.pack(side=BOTTOM, fill=BOTH, expand=True)
        self.chat_box.bind("<Key>", lambda e: "break")
        self.chat_box.tag_config(
            "default", lmargin1=10, lmargin2=10, rmargin=10)
        self.chat_box.tag_config("me", foreground="green", spacing1='5')
        self.chat_box.tag_config("them", foreground="blue", spacing1='5')
        self.chat_box.tag_config("message", foreground="black", spacing1='0')
        self.chat_box.tag_config("system", foreground="grey", spacing1='0',
                                 justify='center', font=(None, 8))

        self.pack(expand=True, fill=BOTH, padx=5, pady=5, ipadx=5, ipady=5)

    def append_to_chat_box(self, time, user, message, tags):
        if user == memory.username:
            user = "我"
        time_info = "%s  %s 说:\n" % (time, user)
        self.chat_box.insert(tk.END, time_info, [tags, 'message'])
        self.chat_box.insert(tk.END, message, [tags, 'default'])
        self.chat_box.insert(tk.END, "\n", [tags, 'message'])
        self.chat_box.update()
        self.chat_box.see(tk.END)

    def send_message(self, _=None):
        stime = dtime.datetime.now()
        time_info = "%s年%s月%s日 %s时%s分%s秒" % (
            stime.year, stime.month, stime.day,
            stime.hour, stime.minute, stime.second)
        message = self.input_textbox.get("1.0", END)
        if not message or message.replace(" ", "").\
                replace("\r", "").replace("\n", "") == '':
            return
        for k1 in memory.friend_list:
            if k1 == (1, self.username):
                self.append_to_chat_box(time_info, "我", message, 'me')
        self.input_textbox.delete("1.0", END)

        # format datetime
        send_message_handler(time_info, message, self.username)
        return 'break'

    def choose_color(self):
        _, self.font_color = colorchooser.askcolor(
            initialcolor=self.font_color)
        self.apply_font_change(None)

    def choose_font_size(self):
        result = simpledialog.askinteger("设置", "请输入字体大小",
                                         initialvalue=self.font_size)
        if result is None:
            return
        self.font_size = result
        self.apply_font_change(None)

    def apply_font_change(self, _):
        try:
            self.input_textbox.tag_config('new', foreground=self.font_color,
                                          font=(None, self.font_size))
            self.input_textbox.tag_add('new', '1.0', END)
        except Exception:
            pass

    def close_window(self):
        del memory.Chat_window[self.username]
        self.master.destroy()

    def update_chatroom_user_list(self, chatroom_name):
        cn = chatroom_name.encode()
        serializeMessage = common_handler.pack_message(common_handler.MessageType.query_room_users, cn)
        client_socket.send_msg(serializeMessage)


def chatroom_user_update(msg):
    chatroom_name = msg[1].decode()
    user_list = msg[2].decode()
    if user_list == "no more user":
        memory.chatroom_user_list = {}
        return
    else:
        _friend_info_lst = user_list.split(" + ")
        tmp = []
        for _i in _friend_info_lst:
            _m = _i.split(":")
            tmp.append((_m[0], _m[1]))
        memory.chatroom_user_list[chatroom_name] = (tmp)
    print(memory.chatroom_user_list)
    for cuser in memory.chatroom_user_list[chatroom_name]:
        memory.Chat_window[chatroom_name].chatroom_user_list.\
            insert(END, cuser[1])


def run(name):
    _tmp = name.split()
    if _tmp[0] == "群":
        username = _tmp[2]
        username = username[1:]
        username = username[:-1]
        nickname = _tmp[1]
    else:
        username = _tmp[1]
        username = username[1:]
        username = username[:-1]
        nickname = _tmp[0]

    try:
        if memory.Chat_window[username]:
            return
    except Exception:
        pass
    root = tk.Toplevel()
    ChatForm(root, username=username, nickname=nickname)
    for i in memory.recv_message:
        if i == username:
            memory.tk_root.update_friend_list(unflag_name=username)
            for _time, _user, _msg, _flag in memory.recv_message[username]:
                memory.Chat_window[username].append_to_chat_box(
                    _time, _user, _msg, _flag)
    root.protocol(
        "WM_DELETE_WINDOW", memory.Chat_window[username].close_window)


def send_message_handler(send_time, msg, username):
    msg = msg.encode()
    send_time = send_time.encode()
    username = username.encode()
    from_user = memory.username.encode()

    for v in memory.friend_list:
        if v[1] == username.decode():
            if v[0] == 2:
                serializeMessage = common_handler.pack_message(
                    common_handler.MessageType.chatroom_message, send_time, username, from_user, msg)
                client_socket.send_msg(serializeMessage)
                return
    serializeMessage = common_handler.pack_message(
        common_handler.MessageType.send_message, send_time, username, from_user, msg)
    client_socket.send_msg(serializeMessage)


def chatmsg_handler(msg):
    from_user = msg[1].decode()
    send_time = msg[2].decode()
    message = msg[3].decode()
    _flag = "them"
    if msg[0] == common_handler.MessageType.broadcast:
        _flag = "system"

    for i in memory.Chat_window:
        # chat window exist
        if i == from_user:
            memory.Chat_window[i].append_to_chat_box(
                send_time, from_user, message, _flag)
            return
    # If not chat with target who msg from someone, save msg to buffer.
    for iii in memory.recv_message:
        if iii == from_user:
            memory.recv_message[from_user].append((send_time, from_user, message, _flag))
            print(memory.recv_message)
            break
    memory.recv_message[from_user] = [(send_time, from_user, message, _flag)]
    memory.tk_root.update_friend_list(flag_name=from_user)


def chatroom_msg_handler(msg):
    send_time = msg[1].decode()
    chatroom_name = msg[2].decode()
    from_user = msg[3].decode()
    message = msg[4].decode()
    _flag = "them"
    for i in memory.Chat_window:
        # chat window exist
        if i == chatroom_name:
            memory.Chat_window[i].append_to_chat_box(
                send_time, from_user, message, _flag)
            return
    # If not chat with target who msg from someone, save msg to buffer.
    for iii in memory.recv_message:
        if iii == chatroom_name:
            memory.recv_message[chatroom_name].append((send_time, from_user, message, _flag))
            print(memory.recv_message)
            break
    memory.recv_message[from_user] = [(send_time, from_user, message, _flag)]
    memory.tk_root.update_friend_list(flag_name=from_user)



if __name__ == "__main__":
    run("jz")
