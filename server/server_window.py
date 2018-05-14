'''
Author:jeremyjone
date:2018-4-9
This is the display window for the server, you can set up ports,
open and close the server, at the same time, you can view the
IP and port of the current connection client.
'''
from tkinter import *
from threading import Thread
import os

from . import memory, server_socket


class ServerForm(Frame):

    def __init__(self, master=None):
        super().__init__(master)
        memory.window = self
        self.master = master
        self.master.resizable(width=False, height=False)
        self.port_frame = Frame(self.master)
        self.list_frame = Frame(self.master)
        self.bottom_frame = Frame(self.master)

        self.ip_label = Label(self.port_frame, text='地址：')
        self.ip_var = StringVar()
        self.ip_var.set('127.0.0.1')
        self.ip_entry = Entry(self.port_frame, textvariable=self.ip_var)
        self.port_label = Label(self.port_frame, text='端口：')
        self.port_var = StringVar()
        self.port_var.set('4444')
        self.port_entry = Entry(self.port_frame, textvariable=self.port_var)
        self.start_server_button = Button(self.port_frame,
                                          text='开启服务器',
                                          command=self.do_open_server)
        self.stop_server_button = Button(self.port_frame,
                                         text='关闭服务器',
                                         command=self.do_close_server)

        self.ip_label.grid(row=0, column=0, ipadx=5)
        self.ip_entry.grid(row=0, column=1, padx=2)
        self.port_label.grid(row=0, column=2, padx=2)
        self.port_entry.grid(row=0, column=3, padx=2, ipadx=5)
        self.start_server_button.grid(row=1, column=0, columnspan=2)
        self.stop_server_button.grid(row=1, column=2, columnspan=2)

        self.list_scorll = Scrollbar(self.list_frame)
        self.list_scorll.pack(side=RIGHT, fill=Y)
        self.user_list = Listbox(self.list_frame,
                                 width=50,
                                 height=30,
                                 yscrollcommand=self.list_scorll.set)
        self.user_list.bind('Visibility', self.add_user_list)
        self.user_list.pack(side=LEFT, ipadx=5, ipady=5, fill=BOTH)
        self.list_scorll.config(command=self.user_list.yview)

        self.infofreshbtn = Button(self.bottom_frame,
                                   text='刷新列表',
                                   command=self.add_user_list)
        self.infofreshbtn.pack(side=RIGHT)

        self.port_frame.grid(row=0, column=0)
        self.list_frame.grid(row=1, column=0)
        self.bottom_frame.grid(row=2, column=0)

    def get_ip(self):
        return self.ip_var.get()

    def get_port(self):
        return self.port_var.get()

    def do_close_server(self):
        memory.server_socket_listener.close()
        memory.server_socket.close()
        memory.online_user.clear()

    def do_open_server(self):
        memory.server_socket_listener = server_socket.\
            server(self.get_ip(), self.get_port())
        t1 = Thread(target=server_socket.server_handler,
                    args=(memory.server_socket_listener,))
        t1.start()
        t1.join(1)

    def add_user_list(self):
        self.user_list.delete("0", END)
        for key in memory.online_user:
            t = memory.online_user[key]
            self.user_list.insert(END, '{:30}{:30}{:15}'
                                  .format(t[0], t[1], t[2]))

    def close_window(self):
        try:
            memory.server_socket.close()
        except Exception:
            pass
        os._exit(0)


def run():
    root = Tk()
    ServerForm(root)
    root.protocol("WM_DELETE_WINDOW", memory.window.close_window)
    root.mainloop()


if __name__ == "__main__":
    run()
