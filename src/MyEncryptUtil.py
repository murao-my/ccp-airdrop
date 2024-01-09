from cryptography.fernet import Fernet

class MyEncryptUtil():

    # キーの生成
    def generate_key(self):
        return Fernet.generate_key()

    # 暗号化
    def encrypt(self, key, message):
        fernet = Fernet(key)
        encrypted = fernet.encrypt(message.encode())
        return encrypted

    # 復号化
    def decrypt(self, key, encrypted_message):
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted_message).decode()
        return decrypted

    def test(self):
        # キーの生成
        key = self.generate_key()
        print("Generated Key:", key.decode())

        # メッセージの暗号化
        message = "seed1 seed2 seed3 seed4 seed5 seed6 seed7 seed8 seed9 seed10 seed11 seed12"
        encrypted_message = self.encrypt(key, message)
        print("Encrypted Message:", encrypted_message)

        # 暗号化されたメッセージの復号化
        decrypted_message = self.decrypt(key, encrypted_message)
        print("Decrypted Message:", decrypted_message)
