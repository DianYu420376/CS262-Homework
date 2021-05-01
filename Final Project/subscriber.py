from Cryptodome.PublicKey import RSA
from Cryptodome import Random
from hashlib import sha512
class Subscriber():
  # each subscriber has these things in its rep
  # list of publisher digital signatures
  # list of respective session keys for each topic that subscriber signs up for
  # source secret key is a RSA generated private key
  # I assume source is a string
  # 
    def __init__(self, name, source_secret_key, source):
        self.name = name
        self.private_key, self.public_key=generate_keypair()
        # each topic belongs to a publisher
        self.topic_lst = []
        this.source=source
        self.source_secret_key =source_secret_key
        self.publisherToCertificate


# (pub_sub_code, action_code, flag, reply, publisher_lst)

        def generate_keypair(bits=2048):
          random_generator = Random.new().read
          rsa_key = RSA.generate(bits, random_generator)
          return rsa_key.exportKey(), rsa_key.publickey().exportKey()

    
    # returns tuple (subscriber_name, subscriber public key, source, signature)
    def submit_registration_request(self, topic_lst):
            # msg is simply Sub||Pksub||S
      def sign_subscriber(msg, source_secret_key):
        # I am unsure what sign/verify algorithm we are using. Here is RSA implementation
        hash = int.from_bytes(sha512(msg).digest(), byteorder='big')
        signature = pow(hash, source_secret_key.d, source_secret_key.n)
        return (hex(signature))

      return (self.name, self.public_key, source, topic_lst, sign_subscriber(self.name+ "||" + str(self.public_key) + "||" + source ))

    # send signature to the server for certification purposes
    def send_signature(self, r):
      hash = int.from_bytes(sha512(r).digest(), byteorder='big')
      signature = pow(hash, self.private_ket.d, self.private_key.n)
      return (hex(signature))
      
    # the topic contains topic id as well as the corresponding publisher name
    def add_topic(self, topic):
      # each item in topic list contains a topic as well as the corresponding publisher       
      # receive session keys for each topic
      topic_lst.add(topic)


    def receive_publisher_list(self, msg):
      # the 5th element in msg is the publisher list
      self.publishers] =msg[4]
