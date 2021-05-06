from authentication_server import Connection, AuthenticationManager, AuthenticationServerThread
from queue import Queue, Empty
import rsa
import os
from helpers import load_private_key, load_public_key, decrypt_message
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
              print(reply)
        else:
          # TODO test this
          print(reply)
    
    def subscribe(self, topic_id_lst):

      outgoing_msg_to_server = (0, 3, topic_id_lst)
      self.server_conn.send(outgoing_msg_to_server) 
      pub_sub_code, action_code, flag, reply = self.client_conn.recv()
      if (flag==1):
          self.topic_dict=reply
          print(reply)
          print("Successfully subscribed to topics")
      else:
        print(reply)


  
    def receive(self):

        # decrypts the message and returns the decoded message
        def decrypt_publisher_msg(encoded_msg):
          # verify the digital signature
          topic_name, cipher, signature = msg
          publisher_key = self.topic_dict[topic_name]['publisher']['publisher_key:']
          if rsa.verify(cipher, signature, publisher_key)==False:
            return 0, ''
          session_key = self.topic_dict[topic_name]['topic_key']
          decoded_msg=decrypt_message(cipher, session_key)
          original_msg = decoded_msg.split(b'||')[1]
          # original_msg is a binary string
          return 1, original_msg.decode('ascii')

        while True:
          for topic in self.topic_dict:
            queue = self.topic_dict[topic]['topic_channel']
            try:
              msg = queue.get(block=False, timeout=None)
              print("A message has been received for topic: ", topic)
              flag, decoded = decrypt_publisher_msg(msg)
              if flag==1:
                print("Identity of sender has been verified and message successfully taken")
                if topic not in self.messages:
                  self.messages[topic]=[decoded]
                else:
                  self.messages[topic].append(decoded)
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


    # create example publisher instance
    pub = Publisher(pub1_server_conn,pub1_client_conn,"topic1", '0123',"source1", "trusted_keys/trusted1",'trusted_keys')
    # register publisher
    pub1_AS_thread = AuthenticationServerThread(pub1_server_conn, pub1_client_conn, authentication_manager)
    pub1_AS_thread.start()
    print("before publisher registered")
    pub.register()
    print("after publisher registered")
    sub.subscribe(['topic1'])

    pub.publish_messeage("Testing")

    sub.receive()



if __name__ == "__main__":

  # Initialization
  # topic_key1 = rsa.newkeys(512)
  # topic_key2 = rsa.newkeys(512)
  # dict1 = {'topic_channel': [], 'topic_key': topic_key1, 'publisher': None, 'subscriber_lst': []}
  # dict2 = {'topic_channel': [], 'topic_key': topic_key2, 'publisher': None, 'subscriber_lst': []}
  # topic_dict = {'topic1': dict1, 'topic2': dict2}
  topic_dict={}
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