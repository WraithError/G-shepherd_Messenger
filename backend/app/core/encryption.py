"""
Encryption Service — Strategy Pattern

Why Strategy?
    So we can swap algorithms (Fernet → AES-GCM → RSA) in the future
    without touching any other file.

Current implementation: Fernet (symmetric encryption)
    - Key derived from SECRET_KEY using SHA-256
    - Same approach as CryptoChat but integrated cleanly
"""

import base64
import hashlib
from abc import ABC, abstractmethod

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


# ── Strategy Interface ─────────────────────────────────────────────────────────

class EncryptionStrategy(ABC):
    """Every encryption algorithm must follow this contract."""

    @abstractmethod
    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string. Returns encrypted string."""
        ...

    @abstractmethod
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a string. Returns original plaintext."""
        ...


# ── Fernet Strategy ────────────────────────────────────────────────────────────

class FernetStrategy(EncryptionStrategy):
    """
    Symmetric encryption using Fernet.
    Key is derived from SECRET_KEY via SHA-256 — no raw keys needed.
    """

    def __init__(self, secret_key: str) -> None:
        # Derive a 32-byte key from the secret using SHA-256
        # Then base64-encode it — Fernet requires this format
        raw_key = hashlib.sha256(secret_key.encode()).digest()
        fernet_key = base64.urlsafe_b64encode(raw_key)
        self._cipher = Fernet(fernet_key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext string → returns encrypted string."""
        return self._cipher.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext string → returns original plaintext."""
        try:
            return self._cipher.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
        except InvalidToken:
            logger.warning("Decryption failed — invalid token or corrupted data")
            raise ValueError("Failed to decrypt message — key mismatch or data corrupted")


# ── Encryption Service ─────────────────────────────────────────────────────────

class EncryptionService:
    """
    The service that all modules use.
    Strategy is injected — swap algorithm without changing this class.
    """

    def __init__(self, strategy: EncryptionStrategy) -> None:
        self._strategy = strategy

    def encrypt(self, plaintext: str) -> str:
        return self._strategy.encrypt(plaintext)

    def decrypt(self, ciphertext: str) -> str:
        return self._strategy.decrypt(ciphertext)


# ── Singleton instance — import this everywhere ────────────────────────────────

encryption = EncryptionService(
    strategy=FernetStrategy(secret_key=settings.SECRET_KEY)
)
