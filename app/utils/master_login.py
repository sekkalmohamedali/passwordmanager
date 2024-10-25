from PyQt6.QtCore import QSettings
import hashlib
import os

class PasswordManager:
    def __init__(self):
        self.settings = QSettings("YourCompany", "YourApp")

    def set_password(self, password):
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        self.settings.setValue("password_salt", salt)
        self.settings.setValue("password_key", key)

    def check_password(self, password):
        stored_salt = self.settings.value("password_salt")
        stored_key = self.settings.value("password_key")
        if stored_salt is None or stored_key is None:
            return False
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), stored_salt, 100000)
        return key == stored_key

    def password_exists(self):
        return self.settings.contains("password_key")