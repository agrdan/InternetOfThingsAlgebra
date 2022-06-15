
from service.CryptoService import CryptoService
import json
crypto = CryptoService()

toEncrypt = "test123"
encrypted = crypto.encrypt(toEncrypt, "testo123")
print(json.dumps(encrypted))
print(str(crypto.decrypt(encrypted, "testo123"), "utf-8"))


"""
import zlib
import base64

with open("mp.jpg", "rb") as file:
    testImage = zlib.compress(file.read())
    b64img = base64.b64encode(testImage)
    file.close()

    print(crypto.encrypt(str(b64img, "utf-8)")))
"""