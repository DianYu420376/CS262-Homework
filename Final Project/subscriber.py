# from Cryptodome.PublicKey import RSA
# from Cryptodome import Random
# from hashlib import sha512
from authentication_server import Connection, AuthenticationManager, AuthenticationServerThread
from queue import Queue, Empty
import rsa
import os
from helpers import load_private_key, load_public_key
from Publisher import Publisher
import time

class Subscriber:
    def __init__(self, sub_name: str,src_name: str, sks:str, trusted_folder:str, client_conn, server_conn):
        self.sub_name = sub_name
        self.pk, self.sk = rsa.newkeys(512)
        self.sks = load_private_key(sks)
        self.topic_lst = []
        self.src_name = src_name
        self.publisher_certificate_lst = []
        self.server_conn = server_conn
        self.client_conn = client_conn
        self.topic_dict={}  # each topic id in the dictionary is mapped to another dictionary
                            # with keys 'publisher', 'topic_key','topic_sk', 'topic_channel'
                            # publisher is also a dictionary  {'publisher_name': publisher_certificate[0], 'publisher_key:': publisher_certificate[1]}
        self.messages={}  # stores the messages received in form of a dictionary 
                          # with topic_id being key and list of messages being value                    

    #TODO write error messages at different steps
    def register(self):
        def generate_certificate():
            msg = self.sub_name + str(self.pk) + self.src_name
            cipher = rsa.sign(msg.encode(), self.sks, 'SHA-1')
            return (self.sub_name,self.pk,self.src_name,cipher)

        certificate = generate_certificate()

        outgoing_msg_to_server = (0, 1, certificate)
        self.server_conn.send(outgoing_msg_to_server) 
        pub_sub_code, action_code, flag, reply = self.client_conn.recv()

        if (flag==1):
            signature = rsa.sign(reply, self.sk, 'SHA-1')
            outgoing_msg_to_server = (0, 2, signature) #2 because now we are in verify stage
            self.server_conn.send(outgoing_msg_to_server)
            pub_sub_code, action_code, flag, reply = self.client_conn.recv()
            if (flag==1):
              print('Signature has been verified, registration succeeds.')
            else:
              # TODO test this
              raise Exception(reply)
        else:
          # TODO test this
          raise Exception(reply)
    
    def subscribe(self, topic_id_lst):
      outgoing_msg_to_server = (0, 3, topic_id_lst)
      self.server_conn.send(outgoing_msg_to_server) 
      pub_sub_code, action_code, flag, reply = self.client_conn.recv()
      if (flag==1):
          self.topic_dict=reply
          print("Successfully subscribed to topics")
      else:
        raise Exception(reply)

    
    def decrypt_publisher_msg(self, msg):
      # step 1: verify the identity of the publisher
       # what is difference between encrypt and encode methods?
      topic_name, cipher, signature = msg
      topic_pk, topic_sk = topic_dict[topic_name]['topic_key']




    # how does a subscriber receive a message?
    # the subscriber receives messages of the form (i, c, s) in its queue
    def receive_from_topic(self, topic_id):
      print("inside receive function")
      queue = topic_dict[topic_id]['topic_channel']
      topic_pubkey, topic_privkey = topic_dict[topic_id]['topic_key']
      # what is the publisher supposed to store?
      topic_key = topic_dict[topic_id]['publisher']

  
    def receive(self):
        while True:
          for topic in topic_dict:
            queue = topic_dict[topic]['topic_channel'][0]
            try:
              msg = queue.get(block=False, timeout=None)
              print("A message has been received for topic: ", topic)
              if topic not in self.messages:
                  self.messages[topic]=[msg]
              else:
                  self.messages[topic].append(msg)
              print(self.messages)                
            except Empty:
                #print('Empty message queue')
                time.sleep(1)
                continue


        

      
      







def main(): 
    sub1_client_conn = Connection()
    sub1_server_conn = Connection()
    pub1_client_conn = Connection()
    pub1_server_conn = Connection()
    sub = Subscriber("naina", "source1", "trusted_keys/trusted1", "trusted_keys", sub1_client_conn, sub1_server_conn)
    
    sub1_AS_thread = AuthenticationServerThread(sub1_server_conn, sub1_client_conn, authentication_manager)
    sub1_AS_thread.start()
    sub.register()
    sub.subscribe(['topic1', 'topic2'])

    # create example publisher instance
    pub = Publisher(pub1_server_conn,pub1_client_conn,"topic2", '0123',"source1", "trusted_keys/trusted1",'trusted_keys')
    # register publisher
    pub1_AS_thread = AuthenticationServerThread(pub1_server_conn, pub1_client_conn, authentication_manager)
    pub1_AS_thread.start()
    print("before publisher registered")
    pub.register()
    print("after publisher registered")
    # example message from a publisher
    pub.publish_messeage("Testing")
    # sub.receive_message('topic1')
    sub.receive()



if __name__ == "__main__":

  # Initialization
  topic_key1 = rsa.newkeys(512)
  topic_key2 = rsa.newkeys(512)
  dict1 = {'topic_channel': [], 'topic_key': topic_key1, 'publisher': None, 'subscriber_lst': []}
  dict2 = {'topic_channel': [], 'topic_key': topic_key2, 'publisher': None, 'subscriber_lst': []}
  topic_dict = {'topic1': dict1, 'topic2': dict2}
  (pubkey1, privkey1) = rsa.newkeys(512)  # public key and privkey for source1
  (pubkey2, privkey2) = rsa.newkeys(512)  # public key and privkey for source1

  source_dict = {'source1': load_public_key("trusted_keys/trusted1.pub"),
                 'source2': load_public_key("trusted_keys/trusted2.pub"),
                 'source3': load_public_key("trusted_keys/trusted2.pub")}
  authentication_manager = AuthenticationManager(topic_dict, source_dict)

  main()





# meeting discussion points
# how are the publisher keys being passed? is the publisher the 
# how is the registration of a subscriber saved? are we gonna run AS in one terminal and 
# use publisher subscribers from the other terminals?
# we are exposing subscriber list, is that okay?