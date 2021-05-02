from queue import Queue, Empty
# import socket
import threading
# from enum import Enum
import time
# import select
# import sys
import rsa
import random


class Connection(Queue):
    def __init__(self):
        super().__init__()

    def recv(self, block=False, timeout=None):
        while True:
            try:
                msg = self.get(block=block, timeout=timeout)
                return msg
            except Empty:
                #print('Empty message queue')
                time.sleep(1)
                continue


    def send(self, msg):
        self.put(msg, block=False)


class ServerSocket(Queue):
    def __init__(self):
        super().__init__()

    def listen(self): #, block=True, timeout=None):
        if self.empty():
            print('no connection detected')
        else:
            client_conn = self.get(block=False, timeout=None) #block=block, timeout=timeout)
            if type(client_conn).__name__ == 'Connection':
                return client_conn # Used for client to receive message from server
            else:
                print('Not a valid connection, please try to reconnect.')
                #return

    def accept(self, client_conn):
        server_conn = Connection()
        client_conn.send(server_conn)
        return server_conn # Used for server to receive message from client



UNCERTIFIED = -1
CERTIFIED = 0
SIGNED = 1

SUCCEED = 1
FAILED = -1


class AuthenticationManager():
    def __init__(self, topic_lst, source_dict):
        self.publisher_lst = {}
        self.subscriber_lst = {}
        self.topic_lst = topic_lst
        self.source_dict = source_dict

    def add_publisher(self, publisher_name, publisher_certificate, publisher_topics = []):
        self.publisher_lst[publisher_name] = (publisher_certificate, publisher_topics)

    def add_subscriber(self, subscriber_name, subscriber_topics = []):
        self.subscriber_lst[subscriber_name] = subscriber_topics

    def get_source_key(self, source):
        return self.source_dict.get(source)


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
        while True:
            msg = self.in_conn.recv()
            #print(msg)
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
        message = machine_id+str(machine_pubkey)+source
        message = message.encode()
        source_pubkey = self.authentication_manager.get_source_key(source) # TODO: finish this part later, check whether the source is reliable and get the public key of the source
        if not source_pubkey:
            flag = FAILED
            reply = 'Unrecognized Source. Certification has failed.'
        else:
            try:
                outcome = rsa.verify(message, signature, source_pubkey)
                flag = SUCCEED
                randnumber = rsa.randnum.read_random_bits(128)
                reply = randnumber #rsa.compute_hash(randnumber,'SHA-1')
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
                    self.out_conn.send((pub_sub_code, action_code, flag, reply, self.authentication_manager.publisher_lst)) # send publisher certificates to subscriber
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

    def server_authentication(self): # TODO: Authenticate the server
        pass

    #def send_publisher_list(self):
    #   pass

    # def remove_publisher/ remove_subscriber...

sk = ServerSocket()
topic_lst = [0,1,2,3]
(pubkey1, privkey1) = rsa.newkeys(512) # public key and privkey for source1
(pubkey2, privkey2) = rsa.newkeys(512) # public key and privkey for source1

source_dict = {'source1': pubkey1, 'source2': pubkey2}
authentication_manager = AuthenticationManager(topic_lst, source_dict)

if __name__ == '__main__':
    print("Main Thread started")
    socket_status = {}
    #while True:
    client_conn = Connection() # IDEALLY THIS LINE SHOULD BE DONE IN A SEPARATE FILE BUT I DON'T KNOW HOW TO DO IT   TAT
    sk.put(client_conn) # IDEALLY THIS LINE SHOULD BE DONE IN A SEPARATE FILE BUT I DON'T KNOW HOW TO DO IT   TAT, THE MAIN DIFFICULTY IS SHARING THE SK THROUGH FILE
    client_conn_AS = sk.listen()
    if client_conn_AS:
        print('got a connection request',type(client_conn_AS))
        server_conn_AS = sk.accept(client_conn_AS)
        server_conn = client_conn.recv() # IDEALLY THIS LINE SHOULD BE DONE IN A SEPARATE FILE BUT I DON'T KNOW HOW TO DO IT   TAT
        print('connection accepted', type(server_conn_AS))
        #socket_status[server_conn.fileno()] = 0
        authentication_thread = AuthenticationServerThread(server_conn_AS, client_conn_AS, authentication_manager)
        authentication_thread.start()


        pub_sub_code = 0 # This is the subscriber

        # Certification step
        action_code = 1
        machine_id = '0123'
        (machine_pubkey,machine_privkey) = rsa.newkeys(512)
        source = 'source1' # Assume that machine 0123 is from source1
        source_pubkey = pubkey1
        source_privkey = privkey1
        message = machine_id + str(machine_pubkey) + source
        message = message.encode()
        signature = rsa.sign(message, source_privkey, 'SHA-1')
        certificate = (machine_id, machine_pubkey, source, signature)
        msg = (pub_sub_code, action_code, certificate)
        server_conn.send(msg)

        # Sign the random number and send it back
        msg = client_conn.recv()
        print(msg)
        flag = msg[2]
        if flag:
            rand_number = msg[3]
            signature = rsa.sign(rand_number, machine_privkey, 'SHA-1')
            action_code = 2
            msg = (pub_sub_code, action_code, signature)
            server_conn.send(msg)

        # Registration complete
        msg = client_conn.recv()
        print(msg)

    time.sleep(1)

    #relay_thread = Message_relay_thread(server_conn, relay_sk)
    #relay_thread.start()

# try to look up user table for logging
# return 0 if succeed, -1 if failed