import rsa
import os

def load_private_key(key_fn):
  with open(key_fn, mode='rb') as privatefile:
      keydata = privatefile.read()
  privkey = rsa.PrivateKey.load_pkcs1(keydata)
  return privkey


def load_public_key(key_fn):
  with open(key_fn, mode='rb') as privatefile:
      keydata = privatefile.read()
  pubkey = rsa.PublicKey.load_pkcs1(keydata)
  return pubkey

