from service.CryptoService import CryptoService

crypto = CryptoService()

toEncrypt = "test123"
encrypted = crypto.encrypt(toEncrypt)
print(str(crypto.decrypt(encrypted), "utf-8"))