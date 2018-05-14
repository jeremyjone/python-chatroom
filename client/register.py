import tkinter as tk
from tkinter import messagebox
from tkinter import *
import struct

from . import memory, client_socket, common_handler, security


class RegisterForm(tk.Frame):
    def do_return(self):
        self.master.destroy()
        memory.Login_window.deiconify()

    def do_register(self):
        username = self.username.get()
        password = self.password.get()
        password_confirmation = self.password_confirmation.get()
        nickname = self.nickname.get()
        if not username:
            messagebox.showerror("出错了", "用户名不能为空")
            return
        if not password:
            messagebox.showerror("出错了", "密码不能为空")
            return
        if not nickname:
            nickname = username
        if password != password_confirmation:
            messagebox.showerror("出错了", "两次密码输入不一致")
            return
        res = client_socket.connect_to_server(str(memory.IP), int(memory.PORT))
        if res == "connect_fail":
            messagebox.showerror("无法连接到服务器", "对不起，无法连接到服务器")
        else:
            memory.sc = res

            # 2 packs
            # First one include length infomation,
            # The second one include complete values information.
            password = security.loop_encrypt(password)
            uname = username.encode()
            pwd = password.encode()
            kname = nickname.encode()

            serializeMessage = common_handler.pack_message(common_handler.MessageType.register, uname, pwd, kname)
            client_socket.send_msg(serializeMessage)
            lg_res = struct.unpack("!L", client_socket.recv_msg(memory.sc))[0]
            if lg_res == common_handler.MessageType.register_successful:
                memory.sc.close()
                messagebox.showinfo("注册成功!", "恭喜您,快上来玩儿啊!")
                self.do_return()
            elif lg_res == common_handler.MessageType.username_taken:
                messagebox.showerror("用户名已存在!", "抱歉,您来晚了,此用户名已有小主了 ^.^!")
            else:
                messagebox.showerror("注册失败!", "可能您的输入方式不对,请换个姿势 ^_^!")

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        # self.memory.tk_reg = self.master

        self.master.resizable(width=False, height=False)
        self.master.geometry('210x170')
        self.master.title("注册账户")

        self.label_1 = Label(self, text="用户名")
        self.label_2 = Label(self, text="密码")
        self.label_3 = Label(self, text="确认密码")
        self.label_4 = Label(self, text="昵称")

        self.username = Entry(self)
        self.password = Entry(self, show="*")
        self.password_confirmation = Entry(self, show="*")
        self.nickname = Entry(self)

        self.label_1.grid(row=0, sticky=E)
        self.label_2.grid(row=1, sticky=E)
        self.label_3.grid(row=2, sticky=E)
        self.label_4.grid(row=3, sticky=E)

        self.username.grid(row=0, column=1, pady=(10, 6))
        self.password.grid(row=1, column=1, pady=(0, 6))
        self.password_confirmation.grid(row=2, column=1, pady=(0, 6))
        self.nickname.grid(row=3, column=1, pady=(0, 6))

        self.btnframe = Frame(self)
        self.regbtn = Button(self.btnframe,
                             text="注册",
                             command=self.do_register)
        self.returnbtn = Button(self.btnframe,
                                text='返回',
                                command=self.do_return)
        self.regbtn.grid(row=0, column=1)
        self.returnbtn.grid(row=0, column=2)
        self.btnframe.grid(row=4, columnspan=2)
        self.pack()


if __name__ == '__main__':
    root = Tk()
    RegisterForm(root)
    root.mainloop()
