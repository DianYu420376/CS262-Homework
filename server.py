import queue
import socket
import threading
from enum import Enum
import time
import select
import sys

lock = threading.Lock()
header_size = 10


class Command(Enum):
    # INITIA = 0
    LOGIN = 1
    LOGOUT = -1
    SENDMSG = 2
    REGISTER = 3
    LIST_USERS = 4
    DELETE_ACCOUNT = 5


# conn.recv(2048)
# msg= "1 username password"
#
# conn.send(f"{len(msgs)}:<{header_size}}".encode('utf-8'))
# message_length = int(conn.recv(header_size).decode('utf-8').strip())
# msgfromclient: length(10 bytes), "command\ndata1\ndata2"
# 1. login username password
# 2. sendmessage username msgs
# 4. list_users
# 5. delete username password
# msgtoclient: length(10bytes) "code\ninfo"
class MSG_CODE(Enum):
    FAILED = -1
    SUCCEED = 0


class Server_thread(threading.Thread):
    def __init__(self, connection):
        threading.Thread.__init__(self)
        self.conn = connection
        # self.lock = threading.Lock()
        # self.user_table = user_table
        # print(users['sf'])
        self.username = ''

    def run(self):
        logged_in = 0
        while True:
            while not logged_in:
                logged_in = self.initialize()
                if logged_in == -2:
                    print(f'user {self.username} seems shutdown the connection, disconncting thread')
                    login_status[self.username] = 0
                    self.conn.shutdown(2)
                    self.conn.close()
                    sys.exit()
            status = self.receive_message()
            if status == -1:
                print(f'user {self.username} seems shutdown the connection, disconncting thread')
                login_status[self.username] = 0
                sys.exit()
            elif status == 2:
                login_status[self.username] = 0
                logged_in = 0;

    def send_message(self):
        pass

    # Initialize connection to login or create account for user
    def initialize(self):
        header = self.conn.recv(header_length)
        if not len(header):
            print("DEBUG: initialization failed")
            return -2
        print(header.decode('utf-8').strip())
        message_length = int(header.decode('utf-8').strip())
        msg = self.conn.recv(message_length).decode('utf-8')
        msgs = msg.split('\n')
        print(msgs)
        try:
            command = int(msgs[0])
        except ValueError:
            print("command received is not integer, conversion failed")
            return -1
        # print(f'DEBUG: Command Received:{command},LOGIN_Command:{Command.LOGIN.value}')
        if command != Command.LOGIN.value and command != Command.REGISTER.value:
            msg = "-1\nInvalid Command, you can only choose to login or register".encode('utf-8')
            data = f"{len(msg):<{header_length}}".encode('utf-8') + msg
            self.conn.send(data)
            # print("Invalid Command")
        else:
            username = msgs[1].strip()
            password = msgs[2].strip()
            if command == Command.LOGIN.value:
                # print(f'DEBUG: start login {username} {password}')
                # print(f"DEBUG: {user_table}")
                if username in user_table and user_table[username] == password:
                    code = MSG_CODE.SUCCEED.value
                    msg = f"{code}\nSuccessful Login".encode('utf-8')
                    data = f"{len(msg):<{header_length}}".encode('utf-8') + msg
                    self.conn.send(data)
                    login_status[username] = 1
                    self.username = username
                    # print("Debug: login successful")
                    socket_status[self.conn.fileno()] = 1
                    return 1
                else:
                    code = MSG_CODE.FAILED.value
                    msg = f"{code}\nInvalid Login, credential doesn't exist or password invalid".encode('utf-8')
                    data = f"{len(msg):<{header_length}}".encode('utf-8') + msg
                    self.conn.send(data)
                    # print("Debug: login failed")
                    return 0
            elif command == Command.REGISTER.value:
                lock.acquire()
                if username in user_table:
                    lock.release()
                    code = MSG_CODE.FAILED.value
                    msg = f"{code}\nThis username has been used".encode('utf-8')
                    data = f"{len(msg):<{header_length}}".encode('utf-8') + msg
                    self.conn.send(data)
                    return 0
                else:
                    user_table[username] = password
                    lock.release()
                    code = MSG_CODE.SUCCEED.value
                    message_queue[username] = queue.Queue()
                    msg = f"{code}\nSuccessful Created and logged in".encode('utf-8')
                    data = f"{len(msg):<{header_length}}".encode('utf-8') + msg
                    self.conn.send(data)
                    login_status[username] = 1
                    self.username = username
                    socket_status[self.conn.server_conn.fileno()] = 1
                    print(f'DEBUG: User:{username} has been created')
                    return 1

    def receive_message(self):
        try:
            header = self.conn.recv(header_length)
        except OSError as e:
            return -1

        # if the received header is empty, than the socket had been closed
        if not len(header):
            return -1
        message_length = int(header.decode('utf=8').strip())
        data = self.conn.recv(message_length).decode('utf-8').strip().split('\n')
        command = data[0]
        command = int(command)
        if command not in Command._value2member_map_:
            data = self.pack_msg(-1, f'invalid command:{command}')
            self.conn.send(data)
        else:
            if command == Command.LIST_USERS.value:
                msg = ''.join('%s ' % user for user in user_table)
                data = self.pack_msg(0, msg)
                self.conn.send(data)
                return 0
            elif command == Command.SENDMSG.value:
                recipient = data[1]
                msg = data[2]
                # if the recipient is invalid
                if recipient not in user_table:
                    data = self.pack_msg(-1, "invalid recipient")
                    self.conn.send(data)
                    print("DEBUG: Invalid Recipient")
                    return 0
                else:
                    lock.acquire()
                    if recipient not in message_queue.keys():
                        message_queue[recipient] = queue.Queue()
                    message_queue[recipient].put(f'{self.username}:{msg}')
                    lock.release()
                    data = self.pack_msg(0, "Sent to recipient")
                    self.conn.send(data)
                    return 0
            elif command == Command.DELETE_ACCOUNT.value:
                if len(data) != 3:
                    data = self.pack_msg(-1, "Invalid deletion detected")
                    self.conn.send(data)
                    return 0
                username = data[1]
                password = data[2]
                if username in user_table and user_table[username] == password:
                    lock.acquire()
                    del user_table[username]
                    login_status[username] = 0
                    lock.release()
                    data = self.pack_msg(0, "account deleted")
                    self.conn.send(data)
                    print(f'user:{username} has been deleted')
                    return 2
                else:
                    data = self.pack_msg(-1, "Invalid credential, deletion failed")
                    self.conn.send(data)
                    return 0
            elif command == Command.LOGOUT.value:
                print(f'User:{self.username} is logging out')
                data = self.pack_msg(0,"Logging out")
                self.conn.send(data)
                return 2



    def pack_msg(self,code, msg):
        msg_encoded = f"{code}\n{msg}".encode('utf-8')
        data = f"{len(msg_encoded):<{header_length}}".encode('utf-8') + msg_encoded
        return data


def pack_msg(code, msg):
    msg_encoded = f"{code}\n{msg}".encode('utf-8')
    data = f"{len(msg_encoded):<{header_length}}".encode('utf-8') + msg_encoded
    return data


class Message_relay_thread(threading.Thread):
    def __init__(self, active_conn,relay_socket):
        threading.Thread.__init__(self)
        self.socket = relay_socket
        self.active_conn = active_conn

    def run(self):
        while self.active_conn.fileno() != -1 and socket_status[self.active_conn.fileno()] == 0:
            time.sleep(0.1)
        if self.active_conn.fileno() == -1:
            print("DEBUG: Relay thread ends before connection")
            sys.exit()
        # print("Logged in Detected, RELAY DEBUG: Running relay thread")
        self.socket.listen(1)
        conn, addr = self.socket.accept()
        # print("RELAY DEBUG: Connection established")
        message_length = int(conn.recv(header_length).decode("utf-8").strip())
        username = conn.recv(message_length).decode("utf-8").strip()
        print(f'start relay thread for user: {username}')
        while self.active_conn.fileno() != -1:
            #if there is the connection is active but login not finished yet
            if login_status[username] == 1:
                try:
                    msg = message_queue[username].get(block=False)
                    data = pack_msg(0,msg)
                    conn.send(data)
                except queue.Empty:
                    time.sleep(1)
                # finally:
            time.sleep(1)
        print(f'User:{username} is disconnected, relay thread exits')
        sys.exit()
command_length = 10
header_length = 10
user_table = {'tester': 'abc123','abc':'abc'}
login_status = {}
buffer = {}
lock = threading.Lock()
ip = '127.0.0.1'
port = 8084
relay_port = 8086
max_connection = 10
message_queue = {}
for key in user_table:
    message_queue[key] = queue.Queue()
sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
relay_sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
relay_sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sk.bind((ip, port))
relay_sk.bind((ip, relay_port))
print("Main Thread started")
socket_status  = {}
while True:
    sk.listen()
    server_conn, server_addr = sk.accept()
    socket_status[server_conn.fileno()] = 0
    server_thread = Server_thread(server_conn)
    server_thread.start()
    relay_thread = Message_relay_thread(server_conn, relay_sk)
    relay_thread.start()

# try to look up user table for logging
# return 0 if succeed, -1 if failed
