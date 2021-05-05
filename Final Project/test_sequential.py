from authentication_server import Connection, AuthenticationServerThread, AuthenticationManager
from subscriber import Subscriber
from Publisher import Publisher
import rsa
from queue import Queue
from helpers import load_private_key, load_public_key
import time


# -------------- Creating three topics ---------------------------------------------------------------
source_dict = {'source1': load_public_key("trusted_keys/trusted1.pub"), 'source2': load_public_key("trusted_keys/trusted2.pub"),
    'source3': load_public_key("trusted_keys/trusted3.pub")}
topic_key1 = rsa.newkeys(512)
topic_key2 = rsa.newkeys(512)
topic_key3 = rsa.newkeys(512)
dict1 = {'topic_channel': [], 'topic_key': topic_key1, 'publisher': None, 'subscriber_lst': []}
dict2 = {'topic_channel': [], 'topic_key': topic_key2, 'publisher': None, 'subscriber_lst': []}
dict3 = {'topic_channel': [], 'topic_key': topic_key3, 'publisher': None, 'subscriber_lst': []}

topic_dict = {'topic1':dict1, 'topic2':dict2, 'topic3':dict3}
authentication_manager = AuthenticationManager(topic_dict, source_dict)

# ------------------------------Creating three publishers ------------------------------------------------

pub1_client_conn = Connection()
pub1_server_conn = Connection()
pub1 = Publisher(pub1_server_conn, pub1_client_conn, "topic1", 'publisher1', "source1", "trusted_keys/trusted1", 'trusted_keys')


pub2_client_conn = Connection()
pub2_server_conn = Connection()
pub2 = Publisher(pub2_server_conn, pub2_client_conn, "topic2", 'publisher2', "source2", "trusted_keys/trusted2", 'trusted_keys')

pub3_client_conn = Connection()
pub3_server_conn = Connection()
pub3 = Publisher(pub3_server_conn, pub3_client_conn, "topic3", 'publisher3', "source3", "trusted_keys/trusted3", 'trusted_keys')


pub1_AS_thread = AuthenticationServerThread(pub1_server_conn, pub1_client_conn, authentication_manager)
pub1_AS_thread.start()
pub1.start()

# pub1.register()
# pub1.publish_messeage("Publisher1 Testing")

pub2_AS_thread = AuthenticationServerThread(pub2_server_conn, pub2_client_conn, authentication_manager)
pub2_AS_thread.start()
pub2.start()
# pub2.register()
# pub2.publish_messeage("Publisher2 Testing")

pub3_AS_thread = AuthenticationServerThread(pub3_server_conn, pub3_client_conn, authentication_manager)
pub3_AS_thread.start()
# pub3.register()
# pub3.publish_messeage("Publisher3 Testing")
pub3.start()

pub1.join()
pub2.join()
pub3.join()

# ------------------------------- Subscribers ------------------------------------------------
# Under construction
sub1_client_conn = Connection()
sub1_server_conn = Connection()
sub1 = Subscriber('subscriber1',"source1","trusted_keys/trusted1", "trusted_keys", sub1_client_conn, sub1_server_conn)

sub2_client_conn = Connection()
sub2_server_conn = Connection()
sub2 = Subscriber('subscriber2',"source2","trusted_keys/trusted2", "trusted_keys", sub2_client_conn, sub2_server_conn)

sub3_client_conn = Connection()
sub3_server_conn = Connection()
sub3 = Subscriber('subscriber3',"source3","trusted_keys/trusted3", "trusted_keys", sub3_client_conn, sub3_server_conn)

sub1_AS_thread = AuthenticationServerThread(sub1_server_conn, sub1_client_conn, authentication_manager)
sub1_AS_thread.start()
sub1.register()
sub1.subscribe(['topic1'])

sub2_AS_thread = AuthenticationServerThread(sub2_server_conn, sub2_client_conn, authentication_manager)
sub2_AS_thread.start()
sub2.register()
sub2.subscribe(['topic2'])

sub3_AS_thread = AuthenticationServerThread(sub3_server_conn, sub3_client_conn, authentication_manager)
sub3_AS_thread.start()
sub3.register()
sub3.subscribe(['topic3'])

pub1.publish_messeage("Publisher1 Testing")
pub2.publish_messeage("Publisher2 Testing")
pub3.publish_messeage("Publisher3 Testing")
