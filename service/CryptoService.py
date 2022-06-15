from base64 import b64encode, b64decode
import hashlib
import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from utils.JSONSerializator import JSONSerializator

class CryptoService:

    def __init__(self):
        pass

    def encrypt(self, plain_text, password):
        salt = get_random_bytes(AES.block_size)

        private_key = hashlib.scrypt(
            password.encode(), salt=salt, n=2 ** 14, r=8, p=1, dklen=32)

        cipher_config = AES.new(private_key, AES.MODE_GCM)
        cipher_text, tag = cipher_config.encrypt_and_digest(bytes(plain_text, 'utf-8'))
        return {
            'cipher_text': b64encode(cipher_text).decode('utf-8'),
            'salt': b64encode(salt).decode('utf-8'),
            'nonce': b64encode(cipher_config.nonce).decode('utf-8'),
            'tag': b64encode(tag).decode('utf-8')
        }

    def decrypt(self, enc_dict, password):
        model = JSONSerializator().serialize(enc_dict)

        salt = b64decode(model.salt)
        cipher_text = b64decode(model.cipher_text)
        nonce = b64decode(model.nonce)
        tag = b64decode(model.tag)

        private_key = hashlib.scrypt(
            password.encode(), salt=salt, n=2 ** 14, r=8, p=1, dklen=32)

        cipher = AES.new(private_key, AES.MODE_GCM, nonce=nonce)
        decrypted = cipher.decrypt_and_verify(cipher_text, tag)
        return str(decrypted, "utf-8")