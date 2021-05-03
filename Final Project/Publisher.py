import rsa
from queue import Queue
import glob
class Publisher:
    def __init__(self,topic_name: str,pub_name: str,src_name: str,pk: str, sks:str,sk:str,trusted_folder:str):
        """Initiaization of Publisher by taking topic name, publisher's name, filename of publisher's pri/pub key
        source's private key
        Args:
            topic_name (str): topic's name
            pub_name (str): pubisher's name
            src_name (str): source's name
            pk (str): public key's filename of publisher
            sk (str): private key's filename of publisher
            sks (str): private key's filename of source
        """
        self.pub_name = pub_name
        # self.topic_list = topic_list
        self.topic_name = topic_name
        self.pk = load_pub_key(pk)
        self.sk = load_private_key(sk)
        self.sks = load_private_key(sks)
        self.src_name = src_name
        self.session_key = ''
        self.msg_q = Queue()
        self.trusted_key_list = load_trusted_key(trusted_folder)

    def load_private_key(key_fn):
        with open(key_fn, mode='rb') as privatefile:
            keydata = privatefile.read()
        privkey = rsa.PrivateKey.load_pkcs1(keydata)
        return privkey

    def load_pub_key(key_fn):
        with open(key_fn, mode='rb') as privatefile:
            keydata = privatefile.read()
        pubkey = rsa.PublicKey.load_pkcs1(keydata)
        return pubkey
        
    def register():
        msg = generate_certificate()
        #TODO send the mssage
        pass

    def generate_certificate():
        msg = self.pub_name+ "||"+self.pk+"||"+self.src_name
        cipher = rsa.sign(msg, self.sks)
        return (self.pub_name,self.pk,self.src_name,cipher)

    def verify_number(r):
        cipher = rsa.sign(r, self.sk)
        return cipher

    def receive_registration_info(session_key, msg_q):
        self.session_key = session_key
        self.msg_q = msg_q

    def publish_messeage(msg):
        if session_key == '':
            print("session key is not estabilished and registered, failed to put message in queue")
            return
        cipher = rsa.encrypt(self.pub_name+"||"+msg, self.session_key)
        sig = rsa.sign(cipher, self.sk)
        self.msg_q.put_nowait((self.topic_name,cipher,sig))
    def load_trusted_key(folder):
        trusted_key = []
        for fn in glob.iglob(folder):
            if 'pub' not in fn:
                key = load_pub_key(fn)
                trusted_key.append(key)
        return trusted_key


        

