from queue import Queue, Empty
# import socket
import threading
# from enum import Enum
# import time
# import select
# import sys


class Connection(Queue):
    def __init__(self):
        super().__init__()

    def recv(self, block=True, timeout=None):
        while True:
            try:
                msg = self.get(block=block, timeout=timeout)
                return client_conn  # Used for client to receive message from server
            except Empty:
                continue

    def send(self, msg):
        self.put(msg, block=False)


class ServerSocket(Queue):
    def __init__(self):
        super().__init__()

    def listen(self, block=True, timeout=None):
        while True:
            try:
                client_conn = self.get(block=block, timeout=timeout)
                return client_conn # Used for client to receive message from server
            except Empty:
                continue

    def accept(self):
        server_conn = Connection()
        return server_conn # Used for server to receive message from client



UNCERTIFIED = -1
CERTIFIED = 0
SIGNED = 1


class AuthenticationManager():
    def __init__(self):
        self.machine_lst = []
        self.publisher_lst = []
        self.subscriber_lst = []


class AuthenticationServerThread(threading.Thread):
    def __init__(self, server_conn, client_conn, authentication_manager):
        threading.Thread.__init__(self)
        self.in_conn = server_conn
        self.out_conn = client_conn
        self.username = ''
        self.status = UNCERTIFIED
        self.authentication_manager = authentication_manager

    def run(self):
        msg = self.in_conn.recv()
        # Interpret message, send it to different functions, e.g. certification, signature, topic
        pass

    def certify(self, certificate):
        # take certificate as an input, if certified, change status and send a random number, else ...
        pass

    def sign(self, signature):
        # check signature
        pass

    def send_topic_key(self, topic_id):
        pass

    def send_publisher_list(self):
        pass

    # def remove_publisher/ remove_subscriber...


sk = ServerSocket()

print("Main Thread started")
socket_status = {}
while True:
    client_conn = sk.listen()
    server_conn = sk.accept()
    #socket_status[server_conn.fileno()] = 0
    authentication_thread = AuthenticationServerThread(server_conn, client_conn)
    authentication_thread.start()

    #relay_thread = Message_relay_thread(server_conn, relay_sk)
    #relay_thread.start()

# try to look up user table for logging
# return 0 if succeed, -1 if failed