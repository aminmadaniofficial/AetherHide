import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class AetherEngine:
    """
    Core engine for AetherHide. 
    Handles AES-256 key derivation, data encryption, and EOF injection.
    """
    def __init__(self):
        # A unique signature to identify where our hidden data begins
        self.marker = b"---AETHER_SIG---"

    def _generate_key(self, password: str, salt: bytes) -> bytes:
        """Derives a secure cryptographic key from a password using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def protect_file(self, input_path: str, message: str, password: str) -> str:
        """Encrypts a message and appends it to a copy of the target file."""
        if not os.path.exists(input_path):
            raise FileNotFoundError("Target file not found.")

        salt = os.urandom(16)
        key = self._generate_key(password, salt)
        cipher = Fernet(key)
        
        encrypted_data = cipher.encrypt(message.encode())
        # Final payload: [SALT (16 bytes)] + [MARKER] + [ENCRYPTED DATA]
        full_payload = salt + self.marker + encrypted_data
        
        # Generating output path (e.g., image_secured.jpg)
        file_dir, file_name = os.path.split(input_path)
        name, ext = os.path.splitext(file_name)
        output_path = os.path.join(file_dir, f"{name}_secured{ext}")

        with open(input_path, "rb") as original:
            file_data = original.read()
        
        with open(output_path, "wb") as secured:
            secured.write(file_data + full_payload)
            
        return output_path

    def recover_data(self, file_path: str, password: str) -> str:
        """Extracts and decrypts hidden data from the target file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found.")

        with open(file_path, "rb") as file:
            data = file.read()
        
        if self.marker not in data:
            raise ValueError("No AetherHide signature found in this file.")
            
        # Splitting by marker to get salt and encrypted payload
        parts = data.split(self.marker)
        encrypted_payload = parts[-1]
        salt = parts[-2][-16:] # The 16 bytes right before the marker is the salt
        
        key = self._generate_key(password, salt)
        cipher = Fernet(key)
        
        try:
            return cipher.decrypt(encrypted_payload).decode()
        except Exception:
            raise ValueError("Decryption failed. Invalid password or corrupted data.")