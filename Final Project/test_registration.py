from authentication_server import Connection, AuthenticationServerThread, AuthenticationManager
from subscriber_windows import Subscriber
from Publisher_windows import Publisher
import rsa
# from queue import Queue
from multiprocessing import Queue
from helpers_windows import load_private_key, load_public_key
import time

if __name__=="__main__":
    num_pub = 200
    num_sub = 20
    source_dict = {'source1': load_public_key("trusted_keys/trusted1.pub"), 'source2': load_public_key("trusted_keys/trusted2.pub"),
        'source3': load_public_key("trusted_keys/trusted3.pub")}
    authentication_manager = AuthenticationManager({}, source_dict)
    conn_list = []
    pub_list = []
    pub_AS = []
    start_t = time.time()
    for i in range(num_pub):
        # pub_client_conn = Connection()
        # pub_server_conn = Connection()
        conn_list.append((Connection(), Connection()))
        pub_list.append(Publisher(conn_list[i][0], conn_list[i][1], "topic"+str(i), 'publisher'+str(i), "source"+str(i%3+1), "trusted_keys/trusted"+str(i%3+1), 'trusted_keys'))
        pub_AS.append(AuthenticationServerThread(conn_list[i][0], conn_list[i][1], authentication_manager))
        pub_AS[i].start()
        pub_list[i].start()
    for i in pub_list:
        i.join()
    for i in pub_AS:
        i.join()
 
    end_t = time.time()
    print(end_t-start_t)


