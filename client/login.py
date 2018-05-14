'''
@Author:jeremyjone
date:2018-5-4

Client interface, starting main interface
'''
import tkinter as tk
from tkinter import messagebox
from tkinter import *
import struct, time

from . import memory, client_socket, contact_form, register, common_handler, security


class LoginForm(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        memory.Login_window = self.master
        self.master.resizable(width=False, height=False)
        self.master.geometry('300x120')
        # bm2 = PhotoImage(file="logo.png")
        # imglabel = Label(self, image=bm2)
        # imglabel.grid(row=0, column=0, columnspan=2)
        self.label_1 = Label(self, text="用户名")
        self.label_2 = Label(self, text="密码")

        self.username = Entry(self)
        self.password = Entry(self, show="*")

        self.label_1.grid(row=1, sticky=E)
        self.label_2.grid(row=2, sticky=E)
        self.username.grid(row=1, column=1, pady=(10, 6))
        self.password.grid(row=2, column=1, pady=(0, 6))

        self.buttonframe = Frame(self)
        self.buttonframe.grid(row=3, column=0, columnspan=2, pady=(4, 6))

        self.logbtn = Button(self.buttonframe,
                             text="登录",
                             command=self.do_login)
        self.logbtn.grid(row=0, column=0)

        self.registerbtn = Button(self.buttonframe,
                                  text="注册",
                                  command=self.do_register)
        self.registerbtn.grid(row=0, column=1)

        self.pack()
        self.master.title("欢迎登陆聊天室...")

    def do_login(self):
        username = self.username.get()
        password = self.password.get()
        password = security.loop_encrypt(password)
        if not username:
            messagebox.showerror("出错了", "用户名不能为空")
            return
        if not password:
            messagebox.showerror("出错了", "密码不能为空")
            return

        res = client_socket.connect_to_server(str(memory.IP), int(memory.PORT))
        if res == "connect_fail":
            messagebox.showerror("无法连接到服务器", "对不起，无法连接到服务器")
        else:
            memory.sc = res

            # 2 packs
            # First one include length infomation,
            # The second one include complete values information.
            uname = username.encode()
            pwd = password.encode()
            serializeMessage = common_handler.pack_message(common_handler.MessageType.login, uname, pwd)
            client_socket.send_msg(serializeMessage)
            lg_res = client_socket.recv_msg(memory.sc)

            # Get result from server
            login_result = common_handler.unpack_message(lg_res)
            if login_result[0] == common_handler.MessageType.login_successful:
                memory.Login_window.destroy()
                memory.Login_window = None
                memory.username = username
                memory.current_user[username] = login_result[1].decode()
                contact_form.run(username)
            else:
                memory.sc.close()
                messagebox.showerror("输入错误!", "对不起,您输入的有误,请重新输入")

    def do_register(self):
        self.master.withdraw()
        reg = tk.Toplevel()
        register.RegisterForm(reg)


def run():
    root = Tk()
    LoginForm(root)
    root.mainloop()


if __name__ == '__main__':
    run()
