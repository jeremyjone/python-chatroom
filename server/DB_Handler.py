'''
author:jeremyjone
date:2018-5-4

This is mysql-DB handler module for chatroom, Receive all
kinds of database operation requests received by the server,
process them and return the results.
'''
import pymysql
import re


class DB_Handler(object):

    def __init__(self):
        self.local = 'localhost'
        self.db_login_name = 'root'
        self.db_login_pswd = '123456'
        self.db = 'chatroom'
        self.userinfo = "userinfo"
        self.chatmsg = "chatmsg"
        self.userfriend = "userfriend"
        self.chatroom = "chatroom"
        self.chatroomuser = "chatroom_user"
        self.charset = "utf8"

    def connect_to_DB(self, sql_statment):
        '''
        Connect to database by base infomation and create database
        handler module, it can receive one SQL and execute.

        If operate successfully return OK, conversely return NG.
        '''
        _ = None
        sql = pymysql.connect(self.local,
                              self.db_login_name,
                              self.db_login_pswd,
                              self.db,
                              charset=self.charset)
        # Create cursor
        cursor = sql.cursor()

        try:
            flag = re.search(r'^(select)\s', sql_statment).group(1)
        except Exception:
            flag = ""

        if flag == "select":
            cursor.execute(sql_statment)
            data = cursor.fetchall()
            _ = data
        else:
            # If not query
            try:
                cursor.execute(sql_statment)
                sql.commit()
                _ = 'OK'
            except Exception as e:
                sql.rollback()
                print(e)
                _ = "NG"
        # close cursor
        cursor.close()
        # close database
        sql.close()
        return _

    def user_exist(self, name):
        '''
        Judge whether the user exists or not.
        '''
        if re.findall(r'^\d+$', name):
            statment = 'select username\
                from %s where id=%s;' % (self.userinfo, name)
        else:
            statment = 'select username\
                from %s where username="%s";' %\
                (self.userinfo, name)
        res = self.connect_to_DB(statment)
        if res:
            return res[0]

    def register(self, name, pswd, nick):
        '''
        User registration, receiving registration information, first
        check whether the username exists, and then fill in the
        registration information into the database.
        '''
        # nick = nick.encode()
        res = self.user_exist(name)
        if res == 'EXIST':
            return 'NAMEEXIST'
        else:
            statment = 'insert into %s (username,\
                     password, nickname, isActive) values ("%s", "%s", "%s", 1);'\
                     % (self.userinfo, name, pswd, nick)
            res2 = self.connect_to_DB(statment)
            if res2 == 'OK':
                return 'OK'
            else:
                return 'NG'

    def login_check(self, name, pswd):
        '''
        Check the user's login information, when received data, return OK
        '''
        statment = 'select username, password from %s\
            where username="%s" and isActive=1;' % (self.userinfo, name)
        res = self.connect_to_DB(statment)
        if res:
            # 判断返回值的密码
            if pswd == res[0][1]:
                return 'OK'
            else:
                return 'NG'

    def change_password(self, name, old_pswd, new_pswd):
        '''
        Change the password, First query the username and password.
        If matching successful, try to change the password. As long
        as modify failed, the return value is NG.
        '''
        statment1 = 'select username, password from %s\
            where username="%s" and isActive=1;' % (self.userinfo, name)
        res = self.connect_to_DB(statment1)
        if res:
            # Judge the password
            if old_pswd == res[0][1]:
                # Modify the password with the current one
                statment2 = 'update %s set password="%s"\
                    where username="%s";' % (self.userinfo, new_pswd, name)
                res2 = self.connect_to_DB(statment2)
                if res2 == 'OK':
                    return 'OK'
        # Return NG as long as no changes have been made
        return 'NG'

    def user_friend(self, name):
        '''
        View friends and return to the list of friends.
        '''
        statment = 'select %s.username, %s.nickname from %s inner join %s\
            on %s.friend_id=%s.id where (%s.user_id=(select id from userinfo\
            where username="%s") and %s.isActive=1);'\
            % (self.userinfo, self.userinfo, self.userfriend, self.userinfo,
               self.userfriend, self.userinfo, self.userfriend, name, self.userfriend)
        res = self.connect_to_DB(statment)
        if res:
            friend_list = []
            for i in res:
                friend_list.append("%s:%s" % (i[0], i[1]))
            return friend_list
        else:
            return "NF"

    def user_add_friend(self, name, friend_name):
        '''
        Add friends to the database.
        '''
        statment1 = 'insert into %s (user_id, friend_id, isActive)\
            values ((select id from %s where username="%s"),\
            (select id from %s where username="%s"), 1);'\
            % (self.userfriend, self.userinfo, name, self.userinfo, friend_name)
        res1 = self.connect_to_DB(statment1)

        statment2 = 'insert into %s (user_id, friend_id, isActive)\
            values ((select id from %s where username="%s"),\
            (select id from %s where username="%s"), 1);'\
            % (self.userfriend, self.userinfo, friend_name, self.userinfo, name)
        res2 = self.connect_to_DB(statment2)

        if res1 == res2 == 'OK':
            return 'OK'
        else:
            return 'NG'

    def user_del_friend(self, name, friend_name):
        '''
        Delete one friend in database.
        In table userfriend, the value of isActive is changed to 0
        '''
        statment1 = 'update %s set isActive=0\
            where user_id=(select id from %s where username="%s") and\
            friend_id=(select id from %s where username="%s");' %\
            (self.userfriend, self.userinfo, name, self.userinfo, friend_name)
        statment2 = 'update %s set isActive=0\
            where user_id=(select id from %s where username="%s") and\
            friend_id=(select id from %s where username="%s");' %\
            (self.userfriend, self.userinfo, friend_name, self.userinfo, name)
        res1 = self.connect_to_DB(statment1)
        res2 = self.connect_to_DB(statment2)
        if res1 == res2 == 'NG':
            return 'NG'
        else:
            return 'OK'

    def get_user_nickname(self, name):
        '''
        Get user's nickname.
        '''
        statment = 'select nickname from %s where username="%s";'\
            % (self.userinfo, name)
        try:
            return self.connect_to_DB(statment)[0]
        except Exception:
            return 'Unknown user'

    def save_msg(self, name, target_user, isRead, msg_type, msg):
        '''
        Save normal chat message, broadcast, chatroom message in DB.
        '''
        statment = 'insert into %s (user_id, target_id,\
            isRead, msg_type, msg, isActive) values (\
            (select id from %s where username="%s"),\
            (select id from %s where username="%s"), %d, %d, "%s", %d);'\
            % (self.chatmsg, self.userinfo, name, self.userinfo,
               target_user, isRead, msg_type, msg, 1)
        res = self.connect_to_DB(statment)
        if res == 'OK':
            return 'OK'
        else:
            return 'NG'

    def get_unread_msg(self, name):
        '''
        Get user's chat message, return msg and change isRead to 0.
        '''
        statment = 'select user_id, send_time, msg_type, msg from %s\
            where target_id=(select id from %s where username="%s" and\
            isRead=1);' % (self.chatmsg, self.userinfo, name)
        res = self.connect_to_DB(statment)
        if res:
            _statment = 'update %s set isRead=0 where target_id=(select id from\
                %s where username="%s" and isRead=1);' % (self.chatmsg,
                                                          self.userinfo, name)
            self.connect_to_DB(_statment)
            return res

    def create_chatroom(self, chatroom_name):
        '''
        Create a new chatroom, first check whether the chatroom exists,
        and then fill in the create information into the database.
        '''
        # chatroom_name = chatroom_name.encode()
        statment1 = 'select chatroom_name\
            from %s where chatroom_name="%s";' % (self.chatroom, chatroom_name)
        res = self.connect_to_DB(statment1)
        if res:
            return 'EXIST'
        else:
            statment2 = 'insert into %s (chatroom_name, isActive) values\
                ("%s", %d);' % (self.chatroom, chatroom_name, 1)
            res1 = self.connect_to_DB(statment2)
            if res1 == "OK":
                return "OK"
            return "NG"

    def chatroom_user(self, chatroom_name, name, user_handler):
        '''
        Manage user in chatroom, when user join a chatroom, insert one record,
        and when user leave a chatroom, its isActive value is changed to 0.
        '''
        # Join operation
        # chatroom_name = chatroom_name.encode()
        if user_handler == 'join':
            statment = 'insert into %s (chatroom_id, user_id, isActive) values\
                ((select id from %s where chatroom_name="%s"),\
                (select id from %s where username="%s"),1);' %\
                (self.chatroomuser, self.chatroom, chatroom_name,
                    self.userinfo, name)
        # Out operation
        elif user_handler == "leave":
            statment = 'update %s set isActive=0 where\
                chatroom_id=(select id from %s where chatroom_name="%s") and\
                user_id=(select id from %s where username="%s");' %\
                (self.chatroomuser, self.chatroom, chatroom_name,
                 self.userinfo, name)
        res = self.connect_to_DB(statment)
        if res == "OK":
            return "OK"
        return "NG"

    def get_username_by_id(self, uid):
        '''
        Get username.
        '''
        statment = 'select username from %s where id="%d" and isActive=1;'\
            % (self.userinfo, uid)
        try:
            return self.connect_to_DB(statment)[0]
        except Exception:
            return 'qurey NG'

    def get_chatroom_user(self, chatroom_name):
        '''
        Get all of users in this chatroom.
        '''
        # chatroom_name = chatroom_name.encode()
        statment = 'select userinfo.username, userinfo.nickname from\
        userinfo where userinfo.id=any(select chatroom_user.user_id from\
        chatroom_user where chatroom_user.chatroom_id=(select chatroom.id\
        from chatroom where chatroom.chatroom_name="%s"));' % chatroom_name

        res = self.connect_to_DB(statment)
        if res:
            friend_list = []
            for i in res:
                friend_list.append("%s:%s" % (i[0], i[1]))
            return friend_list
        else:
            return "NF"

    def query_chatroom(self, name):
        '''
        View room and return to the list of room.
        '''
        # statment_get_id = 'select id from %s where username="%s"' %\
        #     (self.userinfo, name)
        # cid = self.connect_to_DB(statment_get_id)[0]
        # statment_isexist = 'select id from %s where user_id=\
        #     (select id from %s where usernam="%s")' % (
        #     self.chatroom, self.userinfo, name)
        # res = self.connect_to_DB(statment_isexist)

        statment = 'select %s.chatroom_name from %s where %s.id=any(\
            select %s.chatroom_id from %s where %s.user_id=(select id\
            from %s where %s.username="%s"));' % (
            self.chatroom, self.chatroom, self.chatroom,
            self.chatroomuser, self.chatroomuser, self.chatroomuser,
            self.userinfo, self.userinfo, name)
        res = self.connect_to_DB(statment)

        if res:
            chatroom_list = []
            for i in res:
                print(i)
                chatroom_list.append("%s:%s" % ("群", i[0]))
            return chatroom_list
        else:
            return "NF"
