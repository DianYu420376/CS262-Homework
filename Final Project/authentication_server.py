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
    def __init__(self, topic_dict, source_dict):
        # self.publisher_lst = {}
        # self.subscriber_lst = {}
        self.topic_dict = topic_dict # {topic_name: {'topic_channel': list of queues, 'topic_key': topic_key, 'publisher': None, 'subscriber_lst': []}}
        self.source_dict = source_dict # {source_name: source_public_key}

    def add_publisher(self, publisher_certificate, publisher_topics):
        sub_dict = {}
        for publisher_topic in publisher_topics:
            topic = self.topic_dict.get(publisher_topic)
            if not topic:
                flag = FAILED
                reply = 'Topic name doesn\'t exist.'
                return (flag, reply)
            if topic['publisher'] is not None:
                flag = FAILED
                reply = 'This topic has already been registered by another publisher'
                return (flag, reply)
            topic['publisher'] = {'publisher_name': publisher_certificate[0], 'publisher_key:': publisher_certificate[1]}
            sub_dict[publisher_topic] = {'topic_channel': topic['topic_channel'], 'topic_key': topic['topic_key']}
        flag = SUCCEED
        reply = sub_dict
        return (flag, reply)

    def add_subscriber(self, subscriber_certificate, subscriber_topics):
        sub_dict = {}
        for subscriber_topic in subscriber_topics:
            topic = self.topic_dict.get(subscriber_topic)
            if not topic:
                flag = FAILED
                reply = 'Topic name doesn\'t exist.'
                return (flag, reply)
            topic['subscriber_lst'].append({'subscriber_name': subscriber_certificate[0], 'subscriber_key': subscriber_certificate[1]})
            topic['topic_channel'].append(Queue())
            sub_dict[subscriber_topic] = {'topic_channel': topic['topic_channel'][-1], 'publisher': topic['publisher'], 'topic_key': topic['topic_key']}
        flag = SUCCEED
        reply = sub_dict
        return (flag, reply)

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
            elif action_code == 4:
                self.server_authentication(msg)

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
        machine_id = certificate[0] # str
        machine_pubkey = certificate[1] # rsa.Publickey
        source = certificate[2] # str
        signature = certificate[3] # see below
        message = machine_id+str(machine_pubkey)+source
        message = message.encode()
        source_pubkey = self.authentication_manager.get_source_key(source)
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
                # if pub_sub_code == 1:
                #     self.authentication_manager.add_publisher(certificate[0], certificate)
                # elif pub_sub_code == 0:
                #     self.authentication_manager.add_subscriber(certificate[0])
                #     self.out_conn.send((pub_sub_code, action_code, flag, reply, self.authentication_manager.publisher_lst)) # send publisher certificates to subscriber
            except rsa.pkcs1.VerificationError:
                flag = FAILED
                reply = 'Signature verification failed, registration failed'
        self.out_conn.send((pub_sub_code, action_code, flag, reply))

    def send_topic_key(self, msg):
        '''

        :param msg: (pub_sub_code, action_code, topic_id_lst), where topic_id_lst is a list of strings that contains name of topics
        :return:None, AS is going to send a message to self.out_conn, it takes the form: (pub_sub_code, action_code, flag, reply)
                   If flag is success, the reply is going to be a dictionary that contains information of the subscribed or published topics.
                   For publisher, the dictionary takes the form {topic_name(str):{'topic_channel':list of queues, 'topic_key':PublicKey}}
                   For subscriber, the dictionary takes the form {topic_name(str):{'topic_channel':list of queues, 'publisher': {'publisher_name':str, 'publisher_key':PublicKey} ,'topic_key':PublicKey}}
        '''
        pub_sub_code = msg[0]
        action_code = msg[1]
        topic_id_lst = msg[2]
        if self.status != SIGNED:
            flag = FAILED
            reply = 'please register first'
        else:
            machine_certificate = self.buffer[1]
            if pub_sub_code == 1:
                flag,reply = self.authentication_manager.add_publisher(machine_certificate, topic_id_lst)
            elif pub_sub_code == 0:
                flag,reply =self.authentication_manager.add_subscriber(machine_certificate, topic_id_lst)
        self.out_conn.send((pub_sub_code, action_code, flag, reply))

    def server_authentication(self, msg): # TODO: Authenticate the server
        pub_sub_code = msg[0]
        action_code = msg[1]
        rand_number = msg[2]
        signature = rsa.sign(rand_number, machine_privkey, 'SHA-1')
        msg = (pub_sub_code, action_code, signature)
        self.out_conn.send(msg)

    #def send_publisher_list(self):
    #   pass

    # def remove_publisher/ remove_subscriber...

# INITIALIZATION
sk = ServerSocket()
topic_key1 = rsa.newkeys(512)
topic_key2 = rsa.newkeys(512)
dict1 = {'topic_channel': [], 'topic_key': topic_key1, 'publisher': None, 'subscriber_lst': []}
dict2 = {'topic_channel': [], 'topic_key': topic_key2, 'publisher': None, 'subscriber_lst': []}
topic_dict = {'topic1':dict1, 'topic2':dict2}
(pubkey1, privkey1) = rsa.newkeys(512) # public key and privkey for source1
(pubkey2, privkey2) = rsa.newkeys(512) # public key and privkey for source1

source_dict = {'source1': pubkey1, 'source2': pubkey2}
authentication_manager = AuthenticationManager(topic_dict, source_dict)

if __name__ == '__main__':
# A VERY SIMPLE UNIT TEST
    print("Main Thread started")
    #while True:


# ### --- STRUCTURE FOR MAIN TESTING
# pub1_client_conn = Connection()
# pub1_server_conn = Connection()
# sub1_client_conn = Connection()
# sub1_server_conn = Connection()
# ##....
#
# pub1 = Publisher(pub1_client_conn, pub1_server_conn, *Args)
# sub1 = Subscriber(sub1_client_conn, sub1_server_conn, *Args)
# pub1_AS_thread = AuthenticationServerThread(pub1_client_conn, pub1_server_conn, authentication_manager)
# sub1_AS_thread = AuthenticationServerThread(sub1_client_conn, sub1_server_conn, authentication_manager)
# ## ...
#
# pub1_AS_thread.start()
# sub1_AS_thread.start()
# ## ...
# TODO: terminate thread
# ------------------------------------ TEST PUBLISHER ------------------------------------------------------------------
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


        pub_sub_code = 1 # This is a publisher

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
            msg = client_conn.recv()
            print(msg)

        # Registration complete, send topic list to AS
        topic_id_lst = ['topic1']
        action_code = 3
        msg = (pub_sub_code, action_code, topic_id_lst)
        server_conn.send(msg)
        msg = client_conn.recv()
        print(msg)


    time.sleep(1)

# ----------------------------------TEST SUBSCRIBER -----------------------------------------

    client_conn = Connection()  # IDEALLY THIS LINE SHOULD BE DONE IN A SEPARATE FILE BUT I DON'T KNOW HOW TO DO IT   TAT
    sk.put(client_conn)  # IDEALLY THIS LINE SHOULD BE DONE IN A SEPARATE FILE BUT I DON'T KNOW HOW TO DO IT   TAT, THE MAIN DIFFICULTY IS SHARING THE SK THROUGH FILE
    client_conn_AS = sk.listen()
    if client_conn_AS:
        print('got a connection request', type(client_conn_AS))
        server_conn_AS = sk.accept(client_conn_AS)
        server_conn = client_conn.recv()  # IDEALLY THIS LINE SHOULD BE DONE IN A SEPARATE FILE BUT I DON'T KNOW HOW TO DO IT   TAT
        print('connection accepted', type(server_conn_AS))
        # socket_status[server_conn.fileno()] = 0
        authentication_thread = AuthenticationServerThread(server_conn_AS, client_conn_AS, authentication_manager)
        authentication_thread.start()

        pub_sub_code = 0  # This is a subscriber

        # Certification step
        action_code = 1
        machine_id = '0123'
        (machine_pubkey, machine_privkey) = rsa.newkeys(512)
        source = 'source1'  # Assume that machine 0123 is from source1
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
            msg = client_conn.recv()
            print(msg)

            # Registration complete, send topic list to AS
            topic_id_lst = ['topic1']
            action_code = 3
            msg = (pub_sub_code, action_code, topic_id_lst)
            server_conn.send(msg)
            msg = client_conn.recv()
            print(msg)

    #relay_thread = Message_relay_thread(server_conn, relay_sk)
    #relay_thread.start()

# try to look up user table for logging
# return 0 if succeed, -1 if failed