from queue import Queue, Empty
# import socket
import threading
# from enum import Enum
# import time
# import select
# import sys
import rsa
import random


class Connection(Queue):
    def __init__(self):
        super().__init__()

    def recv(self, block=True, timeout=None):
        while True:
            try:
                msg = self.get(block=block, timeout=timeout)
                return client_conn  # Used for client to receive message from server
            except Empty:
                print('Empty message queue')
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

SUCCEED = 1
FAILED = -1


class AuthenticationManager():
    def __init__(self, topic_lst):
        self.publisher_lst = {}
        self.subscriber_lst = {}
        self.topic_lst = topic_lst

    def add_publisher(self, publisher_name, publisher_certificate, publisher_topics = []):
        self.publisher_lst[publisher_name] = (publisher_certificate, publisher_topics)

    def add_subscriber(self, subscriber_name, subscriber_topics = []):
        self.subscriber_lst[subscriber_name] = subscriber_topics


class AuthenticationServerThread(threading.Thread):
    def __init__(self, server_conn, client_conn, authentication_manager):
        threading.Thread.__init__(self)
        self.in_conn = server_conn
        self.out_conn = client_conn
        self.username = ''
        self.status = UNCERTIFIED
        self.buffer = None
        self.authentication_manager = authentication_manager

    def run(self):
        msg = self.in_conn.recv()
        pub_sub_code = msg[0]
        action_code = msg[1]
        if action_code == 1:
            self.certify(msg)
        elif action_code == 2:
            self.sign(msg)
        elif action_code == 3:
            self.send_topic_key(msg)


        # Interpret message, send it to different functions, e.g. certification, signature, topic
        pass

    def certify(self, msg):
        pub_sub_code = msg[0]
        action_code = msg[1]
        certificate = msg[2]
        publisher = certificate[0]
        publisher_pubkey = certificate[1]
        source = certificate[2]
        signature = certificate[3]
        message = publisher+publisher_pubkey+source
        source_pubkey = None # TODO: complete this part
        try:
            outcome = rsa.verify(message, signature, source_pubkey)
            flag = SUCCEED
            randnumber = rsa.randnum.read_random_bits(128)
            reply = rsa.compute_hash(randnumber,'SHA-1')
            self.status = CERTIFIED
            self.buffer = (randnumber, publisher_pubkey)
        except:
            flag = FAILED
            reply = 'Certification has failed'

        self.out_conn.send((pub_sub_code, action_code, flag, reply))

    def sign(self, msg):
        pub_sub_code = msg[0]
        action_code = msg[1]
        if self.status != CERTIFIED:
            flag = FAILED
            reply = 'Please send certification first.'
        else:
            signature = msg[2]
            randnumber = self.buffer[0]
            publisher_pubkey = self.buffer[1]
            outcome = rsa.verify(randnumber, signature, publisher_pubkey)
            if outcome:
                flag = SUCCEED
                reply = 'Signature has been verified, registration succeeed.'
                self.status = SIGNED
                # TODO: add publisher info to authentication manager
            else:
                flag = FAILED
                reply = 'Signature verification failed, registration failed'
        self.out_conn.send((pub_sub_code, action_code, flag, reply))

    def send_topic_key(self, topic_id):
        pub_sub_code = msg[0]
        action_code = msg[1]
        if self.status != SIGNED:
            flag = FAILED
            reply = 'please register first'
        else:
            flag = SUCCEED
            reply = '' # TODO add topic key
        self.out_conn.send((pub_sub_code, action_code, flag, reply))

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