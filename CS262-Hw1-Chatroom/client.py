#!/usr/bin/env python
import sys
import socket
import time
import threading
from threading import Thread


# from SocketServer import ThreadingMixIn

#This is main thread for communicating with server
class ServerThread(Thread):

    def __init__(self, serversocket):
        Thread.__init__(self)
        self.socket = serversocket
        self.help_message = 'This is a chat room app. We support the following command listed below with its corresponding command code:\
                            \n 0. Help\n 1. Log in\n 2. Send message to other users\n 3. Register\n 4. List all registered users\
                            \n 5. Delete account\n -1. Log out'
        # TODO: This message is better put to the server side

    def run(self):
        global log
        global username
        print('Welcome! Connected to the server.')
        print(self.help_message)
        while True:
            starttime = time.time()
            command_code = input(
                " Enter command (enter 0 for help): ")  # TODO: let the user choose from the following action
            curtime = time.time()

            if curtime - starttime > float(TIME_OUT):  # Client times itself out after TIME_OUT idle time
                print(" Your session has been timed out! Please log in again :(")
                self.socket.close()
                log = 0
                sys.exit()

            # send command to the server
            else:
                try:
                    command_code = int(command_code)
                except ValueError:
                    print("command received is not integer, conversion failed")

                if command_code == 0:  # help
                    print(self.help_message)
                    continue
                elif command_code == 1:  # login
                    if log == 1:
                        print('Already logged in.')
                        continue
                    (msg_code, msg, username_) = login(self.socket)
                    print(msg)
                    if msg_code == 0:
                        log = 1
                        username = username_

                elif command_code == 2:  # send messages
                    if log == 0:
                        print('Haven\'t logged in yet. Please first log in or register.')
                        continue
                    else:
                        (msg_code, msg) = send_msg(self.socket)
                        print(msg)

                elif command_code == 3:  # register
                    # if log == 1:
                    #    print('Already logged in， please logout first to register a new account.')
                    #    continue
                    # else:
                    if log == 1:
                        print("You have logged in, please log out then register")
                        continue
                    (msg_code, msg,username_) = register(self.socket)
                    print(msg)
                    if msg_code == 0:
                        log = 1
                        username = username_

                elif command_code == 4:  # get user list
                    if log == 0:
                        print('Haven\'t logged in yet. Please first log in or register.')
                        continue
                    else:
                        (msg_code, msg) = list_users(self.socket)
                        print(msg)

                elif command_code == 5:
                    if log == 0:
                        print('Haven\'t logged in yet. Please first log in or register.')
                        continue
                    else:
                        (msg_code, msg) = delete_account(self.socket, username_)
                        print(msg)
                        if msg_code == 0:
                            print("Account delete, logging out.")
                            log = 0

                elif command_code == -1:
                    if log == 0:
                        print('Already logged out.')
                        continue
                    else:
                        (msg_code, msg) = logout(self.socket)
                        print(msg_code)
                        if msg_code == 0:
                            log = 0
                            print(f'Logging out and exiting')
                            self.socket.shutdown(2)
                            self.socket.close()
                            sys.exit()
                else:
                    print('Please enter a valid command code.')


def login(server_socket):
    # status = 0
    # while status == 0:
    #    number = 0
    try:
        login_username = input("Enter username: ")
        passwd = input("Enter password: ")
        msg = login_username + '\n' + passwd
        packed_msg = pack_msg(1, msg)
        server_socket.send(packed_msg)
        (msg_code, msg) = get_response(server_socket)
        return msg_code, msg, login_username
    except KeyboardInterrupt:
        msg_code = -1
        msg = 'Keyboard Interrupt by User'
        return msg_code, msg, None


def send_msg(server_socket):
    try:
        recipient = input("Which user do you want to send to? :")
        txt_msg = input(("To " + recipient + ' :'))
        msg = recipient + '\n' + txt_msg
        packed_msg = pack_msg(2, msg)
        server_socket.send(packed_msg)
        (msg_code, msg) = get_response(server_socket)
        return msg_code, msg
    except KeyboardInterrupt:
        msg_code = -1
        msg = 'Keyboard Interrupt by User'
        return msg_code, msg


def register(server_socket):
    try:
        register_username = input("Enter username: ").strip()
        passwd = input("Enter password: ")
        msg = register_username + '\n' + passwd
        packed_msg = pack_msg('3', msg)
        print(packed_msg.decode('utf-8'))
        server_socket.send(packed_msg)
        (msg_code, msg) = get_response(server_socket)
        return msg_code, msg, register_username
    except KeyboardInterrupt:
        msg_code = -1
        msg = 'Keyboard Interrupt by User'
        return msg_code, msg, ''


def list_users(server_socket):
    try:
        msg = ''
        packed_msg = pack_msg(4, msg)
        server_socket.send(packed_msg)
        (msg_code, msg) = get_response(server_socket)
        return msg_code, msg
    except KeyboardInterrupt:
        msg_code = -1
        msg = 'Keyboard Interrupt by User'
        return msg_code, msg


def delete_account(server_socket, username_del):
    try:

        # username = input("Enter username of the account you want to delete: ")
        passwd = input("Re-enter password of your account to delete: ")
        msg = username_del + '\n' + passwd
        packed_msg = pack_msg(5, msg)
        server_socket.send(packed_msg)
        (msg_code, msg) = get_response(server_socket)
        return msg_code, msg
    except KeyboardInterrupt:
        msg_code = -1
        msg = 'Keyboard Interrupt by User'
        return msg_code, msg


def logout(server_socket):
    try:
        msg = ''
        packed_msg = pack_msg(-1, msg)
        server_socket.send(packed_msg)
        (msg_code, msg) = get_response(server_socket)
        return msg_code, msg
    except KeyboardInterrupt:
        msg_code = -1
        msg = 'Keyboard Interrupt by User'
        return msg_code, msg


######################################################
def pack_msg(code, msg):
    msg_encoded = f"{code}\n{msg}".encode('utf-8')
    data = f"{len(msg_encoded):<{header_length}}".encode('utf-8') + msg_encoded
    return data


def get_response(server_socket):
    message_length = int(server_socket.recv(header_length).decode('utf-8').strip())
    msg = server_socket.recv(message_length).decode('utf-8')
    msgs = msg.split('\n')
    # print(msgs)
    try:
        msg_code = int(msgs[0])
    except ValueError:
        print("msg_code received is not integer, conversion failed")
        return
    if len(msgs) == 2:
        msg = msgs[1]
    else:
        msg = msgs[1:]
    return msg_code, msg


############################################################

# This thread is only for receiving and displaying chat
class ServerThreadread(Thread):

    def __init__(self, server_socket):
        Thread.__init__(self)
        self.socket = server_socket
        self.s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # print("RELAY threading initialized")
    #  print "New thread started for chat display"

    def run(self):
        global log
        # print("RELAY threading tries to connect")
        # If not logged in, keep waiting for main thread logging
        while not log:
            time.sleep(0.2)
            if self.socket.fileno() == -1:
                print('main socket has been shutdown, shutting down relay thread')
                self.s2.close()
                sys.exit()
        # Add small delay for remote listener
        time.sleep(0.2)
        self.s2.connect((TCP_IP, TCP_PORT2))
        # print("RELAY thread: socket connected")
        # Keep waiting until the current username is setup and sent to remote by protocol.
        while True:
            if self.socket.fileno() == -1:
                self.s2.shutdown(2)
                self.s2.close()
                sys.exit()
            if username is not None:
                msg_encoded = username.encode('utf-8')
                data = f"{len(msg_encoded):<{header_length}}".encode('utf-8') + msg_encoded
                # msg = f'{len(msg)}:<{header_length}'.encode("utf-8")+msg;
                self.s2.send(data)
                # print(f'DEBUG: sent username {data.decode("utf-8")}')
                # welcomemsg = s2.recv(BUFFER_SIZE)

                # chat = "initial"
                # print(welcomemsg)
                break
            time.sleep(0.2)
        # Main loop that keeps relaying messages to server
        while self.socket.fileno() != -1:
            if log == 1:
                header = self.s2.recv(header_length)
                if not len(header):
                    print("RELAY THREAD: Receive 0 Bytes, Sockets seems closed, shutting down locally")
                    self.s2.shutdown(2)
                    self.s2.close()
                    sys.exit()
                message_length = int(header.decode('utf-8').strip())
                chat = self.s2.recv(message_length).decode('utf-8').strip().split('\n')[1]
                chat = "\nNew Message from "+chat
                print(chat)
                time.sleep(0.1)
            else:
                time.sleep(0.1)
        print('main socket has been shutdown, shutting down relay thread')
        self.s2.shutdown(2)
        self.s2.close()
        sys.exit()


TCP_IP = '127.0.0.1'
TCP_PORT = 8084
TCP_PORT2 = 8086
BUFFER_SIZE = 1024
header_length = 10
threads = []
global log
log = 0
global username
username = None
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.connect((TCP_IP, TCP_PORT))

TIME_OUT = 100  # s.recv(BUFFER_SIZE)   #Server exchanges timeout details with client at the start of every socket
count = [1, 2, 3]
status = 1  # login(s)

if status == 1:
    print("logged in")
    try:
        newthread = ServerThread(s)
        # newthread.daemon = True
        newthread.start()
        newthread2 = ServerThreadread(s)
        # newthread2.daemon = True
        newthread2.start()
        threads.append(newthread)
        newthread.join()
        newthread2.join()
        sys.exit()


    except KeyboardInterrupt:
        logout(s)
        sys.exit()






