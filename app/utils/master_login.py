from PyQt6.QtCore import QSettings
import hashlib
import os

from PyQt6.QtWidgets import QMessageBox


class MasterLogin:
    def __init__(self):
        self.settings = QSettings("YourCompany", "YourApp")

    def set_password(self, password):
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        self.settings.setValue("password_salt", salt)
        self.settings.setValue("password_key", key)

    def check_password(self, password):
        stored_salt = self.settings.value("password_salt")
        stored_key = self.settings.value("password_key")
        if stored_salt is None or stored_key is None:
            return False
        key = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), stored_salt, 100000
        )
        return key == stored_key

    def password_reset(self, old_password, new_password):
        # Check if the old password is correct
        if not self.check_password(old_password):
            return False

        # Check if the new password is the same as the old password
        if old_password == new_password:
            return False

        # If the old password is correct and new password is different, set the new password
        self.set_password(new_password)
        return True

    def password_exists(self):
        return self.settings.contains("password_key")
