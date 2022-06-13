from base64 import b64encode, b64decode
import hashlib
import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


class CryptoService:

    def __init__(self):
        #self.pwd = "Međ1kN3t!123"
        self.pwd = "Algebra1!123"
        self.config = None


    def encrypt(self, plain_text):

        salt = "Algebra1PythonDev!".encode('utf-8')
        # use the Scrypt KDF to get a private key from the password
        private_key = hashlib.scrypt(self.pwd.encode(), salt=salt, n=2 ** 14, r=8, p=1, dklen=32)

        test_nonce = b'\x0eL\xa9.\\\xaa\x95\x9eB\x163f\x02g\x8c\x94' # ->
        cipher_config = AES.new(private_key, AES.MODE_SIV)
        cipher_config.nonce = test_nonce
        # return a dictionary with the encrypted text
        cipher_text, tag = cipher_config.encrypt_and_digest(bytes(plain_text, 'utf-8'))

        self.config = {
            'cipher_text': b64encode(cipher_text).decode('utf-8'),
            'salt': b64encode(salt).decode('utf-8'),
            'nonce': b64encode(cipher_config.nonce).decode('utf-8'),
            'tag': b64encode(tag).decode('utf-8')
        }

        return b64encode(cipher_text).decode('utf-8'), self.config


    def decrypt(self, config):
        # decode the dictionary entries from base64
        salt = b64decode(self.config['salt'])
        cipher_text = b64decode(self.config['cipher_text'])
        nonce = b64decode(self.config['nonce'])
        tag = b64decode(self.config['tag'])

        # generate the private key from the password and salt
        private_key = hashlib.scrypt(
            self.pwd.encode(), salt=salt, n=2 ** 14, r=8, p=1, dklen=32)

        # create the cipher config
        cipher = AES.new(private_key, AES.MODE_SIV, nonce=nonce)

        # decrypt the cipher text
        decrypted = cipher.decrypt_and_verify(cipher_text, tag)

        return decrypted