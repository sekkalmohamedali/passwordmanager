from PyQt6.QtCore import QSettings
import hashlib
import os


class MasterLogin:
    def __init__(self):
        self.settings = QSettings("PyQtPasswordManager", "MasterPassword")
        self.db_manager = None

    def set_db_manager(self, db_manager):
        self.db_manager = db_manager
        if self.password_exists():
            key = self.settings.value("password_key")
            self.db_manager.set_encryption_key(key)

    def create_password(self, password):
        """Create new master password"""
        try:
            salt = os.urandom(32)
            key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)

            # Store both salt and key
            self.settings.setValue("password_salt", salt)
            self.settings.setValue("password_key", key)
            self.settings.setValue("master_key", key)  # Add this line

            if self.db_manager:
                self.db_manager.set_encryption_key(key)
            return True
        except Exception as e:
            print(f"Error creating password: {str(e)}")
            return False

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
        """Reset master password and re-encrypt database"""
        if not self.check_password(old_password):
            print("Old password verification failed")
            return False

        try:
            # Get old key
            old_key = self.settings.value("password_key")
            if not old_key:
                print("Could not retrieve old encryption key")
                return False

            # Generate new key
            new_salt = os.urandom(32)
            new_key = hashlib.pbkdf2_hmac(
                "sha256", 
                new_password.encode(), 
                new_salt, 
                100000
            )

            # Verify database manager exists
            if not self.db_manager:
                print("Database manager not initialized")
                return False

            # Re-encrypt database
            if not self.db_manager.reencrypt_database(old_key, new_key):
                print("Database re-encryption failed")
                return False

            # Save new credentials
            self.settings.setValue("password_salt", new_salt)
            self.settings.setValue("password_key", new_key)
            self.db_manager.set_encryption_key(new_key)
            return True

        except Exception as e:
            print(f"Password reset failed: {str(e)}")
            return False

    def password_exists(self):
        return self.settings.contains("password_key")
