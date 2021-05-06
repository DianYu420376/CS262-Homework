
import rsa
from queue import Queue
import glob
from authentication_server import Connection
import helpers 
from authentication_server import Connection, AuthenticationManager, AuthenticationServerThread
import threading

class Publisher(threading.Thread):
    def __init__(self,server_conn:Connection, client_conn:Connection, topic_name: str,pub_name: str,src_name:str,sks:str,trusted_folder:str):
        """Initiaization of Publisher by taking topic name, publisher's name, filename of publisher's pri/pub1 key
        source's private key
        Args:
            topic_name (str): topic's name
            pub_name (str): pubisher's name
            src_name (str): source's name
            pk (str): public key's filename of publisher
            sk (str): private key's filename of publisher
            sks (str): private key's filename of source
        """
        threading.Thread.__init__(self)
        self.pub_name = pub_name
        self.server_conn = server_conn
        self.client_conn = client_conn
        # self.topic_list = topic_list
        self.topic_name = topic_name
        (self.pk, self.sk) = rsa.newkeys(512)
        # self.pk = load_pub_key(pk)
        # self.sk = load_private_key(sk)
        self.sks = helpers.load_private_key(sks)
        self.src_name = src_name
        self.session_key = ''
        self.msg_q_lst = []
        # self.trusted_key_list = load_trusted_key(trusted_folder)
        
        # self.id = id
    def run(self):
        self.register()
        self.publish_messeage(f"{self.pub_name} test publishing")
    def load_private_key(self,key_fn):
        with open(key_fn, mode='rb') as privatefile:
            keydata = privatefile.read()
        privkey = rsa.PrivateKey.load_pkcs1(keydata)
        return privkey

    def load_pub_key(self,key_fn):
        with open(key_fn, mode='rb') as privatefile:
            keydata = privatefile.read()
        pubkey = rsa.PublicKey.load_pkcs1(keydata)
        return pubkey
        
    def register(self):
        certificate = self.generate_certificate()
        # print(msg)
        msg = (1, 1, certificate)
        self.server_conn.send(msg)
        msg = self.client_conn.recv()
        flag = msg[2]
        pub_sub_code = 1 # This is a publisher
        if flag == 1:
            rand_number = msg[3]
            signature = rsa.sign(rand_number, self.sk, 'SHA-1')
            action_code = 2
            msg = (pub_sub_code, action_code, signature)
            self.server_conn.send(msg)
            msg = self.client_conn.recv()
        else:
            print("Publisher register failed")
        #Registration finished, send the topic info
        topic_id_lst = [self.topic_name]
        action_code = 3
        msg = (pub_sub_code, action_code, topic_id_lst)
        self.server_conn.send(msg)
        msg= self.client_conn.recv()
        code = msg[2]
        if code == 1:
            sub_dict = msg[3]
            self.msg_q_lst = sub_dict['topic_channel']
            self.session_key = sub_dict['topic_key']
            # print("finished register")
        

    def generate_certificate(self):
        msg = self.pub_name + str(self.pk) + self.src_name
        cipher = rsa.sign(msg.encode(), self.sks,'SHA-1')
        return (self.pub_name,self.pk,self.src_name,cipher)

    def verify_number(self,r):
        cipher = rsa.sign(r, self.sk)
        return cipher

    # def receive_registration_info(self,session_key, msg_q_lst):
    #     self.session_key = session_key
    #     self.msg_q_lst = msg_q_lst

    def publish_messeage(self,msg):
        if self.session_key == '':
            print("session key is not estabilished and registered, failed to put message in queue")
            return
        cipher = helpers.encrypt_message((self.pub_name+"||"+msg), self.session_key)
        
        sig = rsa.sign(cipher, self.sk,'SHA-1')
        for msg_q in self.msg_q_lst:
            msg_q.put_nowait((self.topic_name,cipher,sig))
        print(f"Message sent from {self.pub_name}")
    def load_trusted_key(self,folder):
        trusted_key = []
        for fn in glob.iglob(folder):
            if 'pub1' not in fn:
                key = helpers.load_pub_key(fn)
                trusted_key.append(key)
        return trusted_key
if __name__ == '__main__':
    source_dict = {'source1': helpers.load_pub_key("trusted_keys/trusted1.pub"), 'source2': helpers.load_pub_key("trusted_keys/trusted2.pub"),
    'source3': helpers.load_pub_key("trusted_keys/trusted2.pub")}
    topic_key1 = rsa.newkeys(512)
    topic_key2 = rsa.newkeys(512)
    dict1 = {'topic_channel': Queue(), 'topic_key': topic_key1, 'publisher': None, 'subscriber_lst': []}
    dict2 = {'topic_channel': Queue(), 'topic_key': topic_key2, 'publisher': None, 'subscriber_lst': []}
    topic_dict = {'topic1':dict1, 'topic2':dict2}
    authentication_manager = AuthenticationManager(topic_dict, source_dict)

    sub1_client_conn = Connection()
    sub1_server_conn = Connection()
    pub1_client_conn = Connection()
    pub1_server_conn = Connection()
    pub = Publisher(pub1_server_conn,pub1_client_conn,"topic1", '0123',"source1", "trusted_keys/trusted1",'trusted_keys')
    # pub1 = Publisher('0213','source1')
    sub1_AS_thread = AuthenticationServerThread(pub1_server_conn, pub1_client_conn, authentication_manager)
    sub1_AS_thread.start()
    pub.register()
    pub.publish_messeage("Testing")
    
    # sub.register()
        

