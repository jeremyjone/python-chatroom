'''
@title: Contact window.
@Author: jeremyjone
date: 2018-5-6

Keep general information for client.
'''
from tkinter import *
import tkinter as tk
from tkinter import messagebox
import time
import struct
from threading import Thread
import os

from . import memory, chat_form, client_socket, common_handler


class contact_window(tk.Frame):
    def on_add_friend(self):
        def do_add_friend():
            friend_name = input_name.get().encode()
            serializeMessage = common_handler.pack_message(common_handler.MessageType.add_friend, friend_name)
            client_socket.send_msg(serializeMessage)
            add_friend_form.destroy()
            messagebox.showinfo('添加好友', '好友请求已发送')

        add_friend_form = Toplevel()
        add_friend_form.title("添加好友")
        lb = Label(add_friend_form, text='要查找的好友名或ID')
        input_name = Entry(add_friend_form)
        btn = Button(add_friend_form, text='走你！', command=do_add_friend)
        lb.pack()
        input_name.pack()
        btn.pack()

    def on_add_room(self):
        def create_room():
            chatroom_name = input_name.get().encode()
            name = memory.username.encode()
            serializeMessage = common_handler.pack_message(common_handler.MessageType.join_room, chatroom_name, name)
            client_socket.send_msg(serializeMessage)
            create_room_form.destroy()

        create_room_form = Toplevel()
        create_room_form.title("加入群")
        lb = Label(create_room_form, text='赶快找到你的组织吧')
        input_name = Entry(create_room_form)
        btn = Button(create_room_form, text='我确定找对了!', command=create_room)
        lb.pack()
        input_name.pack()
        btn.pack()

    def on_create_room(self):
        def create_room():
            chatroom_name = input_name.get().encode()
            serializeMessage = common_handler.pack_message(common_handler.MessageType.create_room, chatroom_name)
            client_socket.send_msg(serializeMessage)
            create_room_form.destroy()

        create_room_form = Toplevel()
        create_room_form.title("创建群")
        lb = Label(create_room_form, text='快给您的后宫起个响亮的名字吧！')
        input_name = Entry(create_room_form)
        btn = Button(create_room_form, text='走你！就是TA了！', command=create_room)
        lb.pack()
        input_name.pack()
        btn.pack()

    def on_list_click(self, e):
        nickname = self.friend_list.get(self.friend_list.curselection())
        chat_form.run(nickname)

    # class get_list_name:
    #     def __init__(self, e):
    #         self.e = e

    #     def get_name():
    #         nickname = memory.tk_root.friend_list.\
    #             get(memory.tk_root.friend_list.curselection())
    #         print(nickname)
    #         if "群" in nickname:
    #             return "退出该群"
    #         else:
    #             return "与TA绝交"

    # def get_list_name(self):
    #     nickname = self.friend_list.get(self.friend_list.curselection())

    def popupmenu(self, e):
        self.delete_menu.post(e.x_root, e.y_root)

    def delete_friend(self):
        name = self.friend_list.get(self.friend_list.curselection())
        _tmp = name.split()
        if _tmp[0] == "群":
            username = _tmp[2]
            username = username[1:]
            username = username[:-1]
            _flag = 2
        else:
            username = _tmp[1]
            username = username[1:]
            username = username[:-1]
            _flag = 1
        do_delete_friend(_flag, username)

    def __init__(self, master=None):
        memory.Contact_window.append(self)
        super().__init__(master)
        self.master = master
        memory.tk_root = self
        master.geometry('%dx%d' % (260, 600))

        self.delete_menu = Menu(self.master, tearoff=0)
        self.delete_menu.add_command(label="与TA绝交", command=self.delete_friend)
        self.delete_menu.add_separator()
        self.base_frame = Frame(self.master)
        self.scroll = Scrollbar(self.base_frame)
        self.scroll.pack(side=RIGHT, fill=Y)
        self.friend_list = Listbox(self.base_frame,
                                   yscrollcommand=self.scroll.set)
        self.friend_list.bind("<Double-Button-1>", self.on_list_click)
        # self.friend_list.bind("<Button-1>", self.get_list_name)
        self.friend_list.bind("<Button-3>", self.popupmenu)
        self.scroll.config(command=self.friend_list.yview)
        self.friend_list.pack(expand=True, fill=BOTH)

        self.button_frame = Frame(self.master)

        self.add_friend = Button(self.button_frame, text="添加好友",
                                 command=self.on_add_friend)
        self.add_friend.pack(side=LEFT, expand=True, fill=X)

        self.add_room = Button(self.button_frame, text="添加群",
                               command=self.on_add_room)
        self.add_room.pack(side=LEFT, expand=True, fill=X)

        self.create_room = Button(self.button_frame, text="创建群",
                                  command=self.on_create_room)
        self.create_room.pack(side=LEFT, expand=True, fill=X)

        self.base_frame.pack(expand=True, fill=BOTH)
        self.button_frame.pack(expand=False, fill=X)

        self.master.title(memory.current_user[memory.username] + " - 联系人列表")

    def update_friend_list(self, flag_name=None, unflag_name=None):
        self.friend_list.delete("0", END)
        _flag = 0
        for t, f in memory.friend_list:
            self.friend_list.insert(
                END, memory.friend_list[(t, f)] + "   (" + f + ")")

            if f == flag_name:
                self.friend_list.itemconfig(_flag, {"fg": "red", "bg": "grey"})
            elif f == unflag_name:
                self.friend_list.itemconfig(_flag, {"fg": "black"})
            _flag += 1

    def close_window(self):
        # Tell server logout.
        flag = b'logout'
        serializeMessage = common_handler.pack_message(common_handler.MessageType.logout, flag)
        client_socket.send_msg(serializeMessage)
        self.master.destroy()
        os._exit(0)


def recive_some_info(msg):
    _flag = msg[0]
    if _flag == common_handler.MessageType.user_not_exist:
        messagebox.showerror("悲剧了!", "您希望添加的好友好像还没出生~!")

    elif _flag == common_handler.MessageType.add_friend_request:
        request_user = msg[1].decode()
        result = messagebox.askyesno("好友请求", request_user + "请求加您为好友，是否同意？")
        if result is False:
            _res = b'NG'
        else:
            _res = b'OK'
        serializeMessage = common_handler.pack_message(
            common_handler.MessageType.confirm_friend_request, _res, memory.username.encode(), request_user.encode())
        client_socket.send_msg(serializeMessage)

    elif _flag == common_handler.MessageType.add_friend_result:
        if msg[1].decode() == "OK":
            messagebox.showinfo("恭喜您！", msg[2].decode() + "愿意跟您促膝长谈啦!")
        else:
            messagebox.showinfo("不走运", msg[2].decode() + "不愿意搭理你!")

    elif _flag == common_handler.MessageType.join_leave_chatroom:
        if msg[1] == b"OK":
            username = memory.username.encode()
            serializeMessage = common_handler.pack_message(common_handler.MessageType.query_friend, username)
            memory.sc.send(serializeMessage)
        else:
            messagebox.showerror("悲剧了!", "您希望添加的群组像空气~!")

    elif _flag == common_handler.MessageType.delete_friend_failed:
        messagebox.showinfo("对不住", msg[1].decode() + "删除失败！")


def show(msg):
    friend_list_handler(msg)


def friend_list_handler(msg):
    friend_list = msg[1].decode()
    chatroom_list = msg[2].decode()
    memory.friend_list.clear()
    if friend_list != "no friend":
        _friend_info_lst = friend_list.split(" + ")
        for _i in _friend_info_lst:
            _fl = _i.split(":")
            memory.friend_list[(1, _fl[0])] = _fl[1]
    if chatroom_list != "no chatroom":
        _chat_info_lst = chatroom_list.split(" + ")
        for _i in _chat_info_lst:
            _cl = _i.split(":")
            memory.friend_list[(2, _cl[1])] = "群  " + _cl[1]
    memory.tk_root.update_friend_list()


def run(username):
    # Request friends list
    root = Tk()
    contact_window(root)

    t = Thread(target=client_socket.keep_recv)
    memory.recv_msg_thread = t
    t.start()

    time.sleep(0.1)
    username = username.encode()
    serializeMessage = common_handler.pack_message(common_handler.MessageType.query_friend, username)
    memory.sc.send(serializeMessage)
    root.protocol("WM_DELETE_WINDOW", memory.tk_root.close_window)
    root.mainloop()
    t.join()


def chatroom_handler(msg):
    m = msg[1].decode()

    if m == "EXIST":
        messagebox.showerror("遗憾了~", "真遗憾,您希望的名字已被别的小主相中,赶快换一个吧!")
    elif m == "NG":
        messagebox.showerror("悲剧了!", "悲剧了,您到底干了啥,没成功耶!")
    elif m == "OK":
        chatroom_name = msg[2].decode()
        memory.friend_list[(2, chatroom_name)] = "群  " + chatroom_name
        memory.tk_root.update_friend_list()


def do_delete_friend(flag, username):
    if flag == 1:
        target_user = username.encode()
        me = memory.username.encode()
        serializeMessage = common_handler.pack_message(
            common_handler.MessageType.delete_friend, target_user, me)
        client_socket.send_msg(serializeMessage)
    else:
        # Leave chatroom.
        pass
