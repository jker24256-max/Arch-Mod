import os
import base64
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class VaultEncryptor:
    def __init__(self, vault_path="vault.db"):
        self.vault_path = vault_path
        self.salt_length = 16
        self.iterations = 100000

    def derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive a Fernet-compatible base64 key from a master password and salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.iterations,
        )
        derived = kdf.derive(password.encode())
        return base64.urlsafe_b64encode(derived)

    def initialize_vault(self, password: str) -> bool:
        """Create a new empty vault encrypted with the password."""
        if os.path.exists(self.vault_path):
            return False
        
        salt = os.urandom(self.salt_length)
        key = self.derive_key(password, salt)
        fernet = Fernet(key)
        
        default_data = {
            "passwords": [],
            "notes": [],
            "ssh_keys": [],
            "api_keys": []
        }
        
        serialized = json.dumps(default_data).encode()
        encrypted_data = fernet.encrypt(serialized)
        
        with open(self.vault_path, "wb") as f:
            f.write(salt + encrypted_data)
        return True

    def load_vault(self, password: str) -> dict:
        """Decrypt and load the vault. Returns data dict if successful, None otherwise."""
        if not os.path.exists(self.vault_path):
            raise FileNotFoundError("Vault file does not exist.")
            
        with open(self.vault_path, "rb") as f:
            file_content = f.read()
            
        if len(file_content) < self.salt_length:
            raise ValueError("Vault file is corrupted.")
            
        salt = file_content[:self.salt_length]
        encrypted_data = file_content[self.salt_length:]
        
        try:
            key = self.derive_key(password, salt)
            fernet = Fernet(key)
            decrypted = fernet.decrypt(encrypted_data)
            return json.loads(decrypted.decode())
        except Exception:
            return None

    def save_vault(self, password: str, data: dict) -> bool:
        """Encrypt and save data to the vault."""
        salt = os.urandom(self.salt_length)
        key = self.derive_key(password, salt)
        fernet = Fernet(key)
        
        serialized = json.dumps(data).encode()
        encrypted_data = fernet.encrypt(serialized)
        
        with open(self.vault_path, "wb") as f:
            f.write(salt + encrypted_data)
        return True

    def encrypt_external_file(self, password: str, file_path: str, dest_path: str) -> bool:
        """Encrypts an external file and saves it to dest_path."""
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            salt = os.urandom(self.salt_length)
            key = self.derive_key(password, salt)
            fernet = Fernet(key)
            encrypted = fernet.encrypt(data)
            with open(dest_path, "wb") as f:
                f.write(salt + encrypted)
            return True
        except Exception:
            return False

    def decrypt_external_file(self, password: str, file_path: str, dest_path: str) -> bool:
        """Decrypts a file from file_path and saves it to dest_path."""
        try:
            with open(file_path, "rb") as f:
                file_content = f.read()
            if len(file_content) < self.salt_length:
                return False
            salt = file_content[:self.salt_length]
            encrypted_data = file_content[self.salt_length:]
            key = self.derive_key(password, salt)
            fernet = Fernet(key)
            decrypted = fernet.decrypt(encrypted_data)
            with open(dest_path, "wb") as f:
                f.write(decrypted)
            return True
        except Exception:
            return False
