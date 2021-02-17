#!/usr/bin/env python
import sys
import socket
import time
import threading
from threading import Thread
# from SocketServer import ThreadingMixIn



class ServerThread(Thread):
 
    def __init__(self,socket):
        Thread.__init__(self)
        self.socket = socket
        self.help_message = 'This is a chat room app. We support the following command listed below with its corresponding command code:\
                            \n 0. Help\n 1. Log in\n 2. Send message to other users\n 3. Register\n 4. List all registered users\
                            \n 5. Delete account\n -1. Log out'
        # TODO: This message is better put to the server side

    def run(self):
        global log
        print('Welcome! Connected to the server.')
        print(self.help_message)
        while True:
            starttime = time.time()
            command_code = input(" Enter command (enter 0 for help): ")  # TODO: let the user choose from the following action
            curtime = time.time()
        
            if curtime - starttime > float(TIME_OUT):     #Client times itself out after TIME_OUT idle time
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

                if command_code == 0: # help
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
                    if log == 1:
                        print('Already logged in， please logout first to register a new account.')
                        continue
                    else:
                        (msg_code, msg) = register(self.socket)
                        print(msg)

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
                        (msg_code, msg) = delete_account(self.socket)
                        print(msg)

                elif command_code == -1:
                    if log==0:
                        print('Already logged out.')
                        continue
                    else:
                        (msg_code, msg) = logout(self.socket)
                        print(msg)
                        if msg_code == 0:
                            log = 0
                            self.socket.close()
                            sys.exit()
                else:
                    print('Please enter a valid command code.')


             
def login(socket):
    #status = 0
    #while status == 0:
    #    number = 0
    try:
        username = input("Enter username: ")
        passwd = input("Enter password: ")
        msg = username + '\n'+passwd
        packed_msg = pack_msg(1, msg)
        socket.send(packed_msg)
        (msg_code, msg) = get_response(socket)
        return msg_code, msg, username
    except KeyboardInterrupt:
        msg_code = -1
        msg = 'Keyboard Interrupt by User'
        return msg_code, msg, None

def send_msg(socket):
    try:
        username = input("Which user do you want to send to? :")
        txt_msg = input(("To " + username + ' :'))
        msg = username + '\n'+txt_msg
        packed_msg = pack_msg(2, msg)
        socket.send(packed_msg)
        (msg_code, msg) = get_response(socket)
        return msg_code, msg
    except KeyboardInterrupt:
        msg_code = -1
        msg = 'Keyboard Interrupt by User'
        return msg_code, msg

def register(socket):
    try:
        username = input("Enter username: ")
        passwd = input("Enter password: ")
        msg = username + '\n'+passwd
        packed_msg = pack_msg('3', msg)
        print(packed_msg.decode('utf-8'))
        socket.send(packed_msg)
        (msg_code, msg) = get_response(socket)
        return msg_code, msg
    except KeyboardInterrupt:
        msg_code = -1
        msg = 'Keyboard Interrupt by User'
        return msg_code, msg

def list_users(socket):
    try:
        msg = ''
        packed_msg = pack_msg(4, msg)
        socket.send(packed_msg)
        (msg_code, msg) = get_response(socket)
        return msg_code, msg
    except KeyboardInterrupt:
        msg_code = -1
        msg = 'Keyboard Interrupt by User'
        return msg_code, msg

def delete_account(socket):
    try:
        username = input("Enter username of the account you want to delete: ")
        passwd = input("Enter password of the account you want to delete: ")
        msg = username + '\n'+passwd
        packed_msg = pack_msg(5, msg)
        socket.send(packed_msg)
        (msg_code, msg) = get_response(socket)
        return msg_code, msg
    except KeyboardInterrupt:
        msg_code = -1
        msg = 'Keyboard Interrupt by User'
        return msg_code, msg

def logout(socket):
    try:
        msg = ''
        packed_msg = pack_msg(-1, msg)
        socket.send(packed_msg)
        (msg_code, msg) = get_response(socket)
        return msg_code, msg
    except KeyboardInterrupt:
        msg_code = -1
        msg = 'Keyboard Interrupt by User'
        return msg_code, msg

######################################################
def pack_msg(code,msg):
    msg_encoded = f"{code}\n{msg}".encode('utf-8')
    data = f"{len(msg_encoded):<{header_length}}".encode('utf-8') + msg_encoded
    return data

def get_response(socket):
    message_length = int(socket.recv(header_length).decode('utf-8').strip())
    msg = socket.recv(message_length).decode('utf-8')
    msgs = msg.split('\n')
    print(msgs)
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
 
    def __init__(self,socket):
        Thread.__init__(self)
        self.socket = socket
        
      #  print "New thread started for chat display"
 
    def run(self):
        
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2.connect((TCP_IP, TCP_PORT2))
        msg = f'{len(username.encode("utf-8"))}:<{header_length}' + username.encode('utf-8')
        s2.send(msg)
        welcomemsg = s2.recv(BUFFER_SIZE)
        chat = "initial"
        print(welcomemsg)
        
        while True:
            if log == 1:
              #  print "inside loop"
                chat = s2.recv(BUFFER_SIZE)
                print(chat)
                time.sleep(5)
                
            if log == 0:
              #  print "going to exit"
                s2.close()
                sys.exit()


        


 
 
TCP_IP = '127.0.0.1'
TCP_PORT = 8080
TCP_PORT2 = 8082
BUFFER_SIZE = 1024
header_length = 10
threads = []
global log
log = 0
global username
username = None
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

TIME_OUT = 100 #s.recv(BUFFER_SIZE)   #Server exchanges timeout details with client at the start of every socket
count = [1, 2, 3]
status = 1 #login(s)
        
if status == 1:
    print("logged in")
    try:
        newthread = ServerThread(s)
        newthread.daemon = True
        newthread.start()
        #s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #s2.connect((TCP_IP, TCP_PORT2))
        #newthread2 = ServerThreadread(s2)
        #newthread2.daemon = True
        #newthread2.start()
        threads.append(newthread)
        #threads.append(newthread2)
        while True:
            for t in threads:
                t.join(600)
                if not t.is_alive():
                    break
            break        
            
            
    except KeyboardInterrupt:
        logout(s)
        sys.exit()
        log = 0
    
   
            
    

 

