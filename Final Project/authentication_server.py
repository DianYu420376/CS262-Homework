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
                return msg
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
                if type(client_conn).__name__ == 'Connection':
                    return client_conn # Used for client to receive message from server
                else:
                    print('Not a valid connection, please try to reconnect.')
                    return
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

        # TODO: what if new publisher joined and the AS need to inform subscribers of that change?
        # if self.status == SIGNED:
        #     self.update_publisher_lst

    def certify(self, msg):
        '''
        :param msg: (pub_sub_code, action_code, certificate), where certificate is a 4-dimensional tuple: certification = (machine_id, machine_pubkey, source, signature)
        :return: None, AS is going to send a message to self.out_conn, message takes the form: (pub_sub_code, action_code, flag, reply), where reply is going to be the hash code of a random number if certification has succeed
        '''
        pub_sub_code = msg[0]
        action_code = msg[1]
        certificate = msg[2]
        machine_id = certificate[0]
        machine_pubkey = certificate[1]
        source = certificate[2]
        signature = certificate[3]
        message = machine_id+machine_pubkey+source
        source_pubkey = get_source_key(source, self.authentication_manager) # TODO: finish this part later, check whether the source is reliable and get the public key of the source
        if not source_pubkey:
            flag = FAILED
            reply = 'Unrecognized Source. Certification has failed.'
        else:
            try:
                outcome = rsa.verify(message, signature, source_pubkey)
                flag = SUCCEED
                randnumber = rsa.randnum.read_random_bits(128)
                reply = rsa.compute_hash(randnumber,'SHA-1')
                self.status = CERTIFIED
                self.buffer = (randnumber, certificate)
            except rsa.pkcs1.VerificationError:
                flag = FAILED
                reply = 'Cannot verify signature. Certification has failed'

        self.out_conn.send((pub_sub_code, action_code, flag, reply))

    def sign(self, msg):
        '''
        :param msg: (pub_sub_code, action_code, signature)
        :return: None, AS is going to send a message to self.out_conn.
                    If the message is for the publisher, it takes the form: (pub_sub_code, action_code, flag, reply)
                    If the message is for the subcriber, it takes the form: (pub_sub_code, action_code, flag, reply, publisher_lst), where publisher_lst is a list of registered publisher with their certificates.
        '''
        pub_sub_code = msg[0]
        action_code = msg[1]
        if self.status != CERTIFIED:
            flag = FAILED
            reply = 'Please send certification first.'
        else:
            signature = msg[2]
            randnumber = self.buffer[0]
            certificate = self.buffer[1]
            machine_pubkey = certificate[1]
            try:
                outcome = rsa.verify(randnumber, signature, machine_pubkey)
                flag = SUCCEED
                self.status = SIGNED
                reply = 'Signature has been verified, registration succeed.'
                if pub_sub_code == 1:
                    self.authentication_manager.add_publisher(certificate[0], certificate)
                elif pub_sub_code == 0:
                    self.authentication_manager.add_subscriber(certificate[0])
                    self.outconn.send((pub_sub_code, action_code, flag, reply, self.authentication_manager.publisher_lst)) # send publisher certificates to subscriber
            except rsa.pkcs1.VerificationError:
                flag = FAILED
                reply = 'Signature verification failed, registration failed'
        self.out_conn.send((pub_sub_code, action_code, flag, reply))

    def send_topic_key(self, msg):
        pub_sub_code = msg[0]
        action_code = msg[1]
        topic_id_lst = msg[2]
        if self.status != SIGNED:
            flag = FAILED
            reply = 'please register first'
        else:
            flag = SUCCEED
            reply = {topic_id:self.authentication_manager.topic_lst.get(topic_id) for topic_id in topic_id_lst}
            machine_id = self.buffer[1][0]
            if pub_sub_code == 1:
                [self.authentication_manager.publisher_lst[machine_id].append(topic_id) for topic_id in topic_id_lst
                    if topic_id not in self.authentication_manager.publisher_lst[machine_id]]  # add topic_id to publisher_list
            elif pub_sub_code == 0:
                [self.authentication_manager.subscriber_lst[machine_id].append(topic_id) for topic_id in topic_id_lst
                    if topic_id not in self.authentication_manager.subscriber_lst[machine_id]]  # add topic_id to publisher_list
        self.out_conn.send((pub_sub_code, action_code, flag, reply))

    #def send_publisher_list(self):
    #   pass

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