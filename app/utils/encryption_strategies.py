from abc import ABC, abstractmethod
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

class EncryptionStrategy(ABC):
    @abstractmethod
    def encrypt(self, data: str) -> str:
        pass

    @abstractmethod
    def decrypt(self, encrypted_data: str) -> str:
        pass
    
    @abstractmethod
    def initialize_key(self, key: bytes) -> None:
        pass

class FernetEncryptionStrategy(EncryptionStrategy):
    def __init__(self):
        self.cipher = None

    def initialize_key(self, key: bytes) -> None:
        print(f"Initializing Fernet with key length: {len(key)}")
        if isinstance(key, str):
            key = key.encode()
        key = base64.urlsafe_b64encode(key[:32].ljust(32, b'\0'))
        self.cipher = Fernet(key)
        print("Fernet initialization successful")

    def encrypt(self, data: str) -> str:
        if not self.cipher:
            raise ValueError("Encryption key not initialized")
        
        # Convert to bytes if string
        if isinstance(data, str):
            data = data.encode()
            
        # Encrypt and return as string
        encrypted = self.cipher.encrypt(data)
        return encrypted.decode() if isinstance(encrypted, bytes) else encrypted

    def decrypt(self, encrypted_data: str) -> str:
        if not self.cipher:
            raise ValueError("Encryption key not initialized")
            
        # Convert to bytes if string
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
            
        # Decrypt and return as string
        decrypted = self.cipher.decrypt(encrypted_data)
        return decrypted.decode() if isinstance(decrypted, bytes) else decrypted

class AESEncryptionStrategy(EncryptionStrategy):
    def __init__(self):
        self.key = None
        self.iv = os.urandom(16)  # Initialization vector

    def initialize_key(self, key: bytes) -> None:
        print(f"Initializing AES with key length: {len(key)}")
        try:
            if len(key) != 32:  # AES-256 requires 32 bytes
                padded_key = key.ljust(32, b'\0')
                self.key = padded_key[:32]
            else:
                self.key = key
            self.iv = os.urandom(16)
            print("AES initialization successful")
        except Exception as e:
            print(f"AES initialization failed: {str(e)}")
            raise

    def encrypt(self, data: str) -> str:
        if not self.key:
            raise ValueError("Encryption key not initialized")
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv))
        encryptor = cipher.encryptor()
        # Add padding and encrypt
        padded_data = self._pad(data.encode())
        ct = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(self.iv + ct).decode()

    def decrypt(self, encrypted_data: str) -> str:
        if not self.key:
            raise ValueError("Encryption key not initialized")
        
        encrypted_bytes = base64.b64decode(encrypted_data)
        iv = encrypted_bytes[:16]
        ct = encrypted_bytes[16:]
        
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ct) + decryptor.finalize()
        
        # Remove padding
        padding_length = padded_data[-1]
        data = padded_data[:-padding_length]
        return data.decode()

    def _pad(self, data: bytes) -> bytes:
        # PKCS7 padding
        padding_length = 16 - (len(data) % 16)
        padding = bytes([padding_length] * padding_length)
        return data + padding