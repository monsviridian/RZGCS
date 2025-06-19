"""
Verbindungssicherheit
"""

from typing import Optional
import hashlib
import hmac
from cryptography.fernet import Fernet

class ConnectionSecurity:
    """Verbindungssicherheit"""
    
    def __init__(self):
        """Initialisiert die Verbindungssicherheit"""
        self.encryption_enabled = False
        self.encryption_key: Optional[bytes] = None
        self.fernet: Optional[Fernet] = None
    
    def enable_encryption(self, key: bytes) -> None:
        """
        Aktiviert die Verschlüsselung
        
        Args:
            key: Verschlüsselungsschlüssel
        """
        self.encryption_enabled = True
        self.encryption_key = key
        self.fernet = Fernet(key)
    
    def encrypt_message(self, message: bytes) -> bytes:
        """
        Verschlüsselt eine Nachricht
        
        Args:
            message: Zu verschlüsselnde Nachricht
            
        Returns:
            Verschlüsselte Nachricht
        """
        if not self.encryption_enabled or not self.fernet:
            return message
        
        try:
            return self.fernet.encrypt(message)
        except Exception as e:
            print(f"Encryption error: {str(e)}")
            return message
    
    def decrypt_message(self, encrypted_message: bytes) -> bytes:
        """
        Entschlüsselt eine Nachricht
        
        Args:
            encrypted_message: Verschlüsselte Nachricht
            
        Returns:
            Entschlüsselte Nachricht
        """
        if not self.encryption_enabled or not self.fernet:
            return encrypted_message
        
        try:
            return self.fernet.decrypt(encrypted_message)
        except Exception as e:
            print(f"Decryption error: {str(e)}")
            return encrypted_message
    
    def generate_key(self) -> bytes:
        """
        Generiert einen neuen Verschlüsselungsschlüssel
        
        Returns:
            Generierter Schlüssel
        """
        return Fernet.generate_key()
    
    def verify_message(self, message: bytes, signature: bytes) -> bool:
        """
        Überprüft die Signatur einer Nachricht
        
        Args:
            message: Nachricht
            signature: Signatur
            
        Returns:
            True wenn die Signatur gültig ist, sonst False
        """
        if not self.encryption_key:
            return False
        
        expected_signature = hmac.new(
            self.encryption_key,
            message,
            hashlib.sha256
        ).digest()
        
        return hmac.compare_digest(signature, expected_signature) 