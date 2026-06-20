"""Security layer — encryption, secrets, zero-trust foundations."""

import base64
import hashlib
import os
from datetime import UTC, datetime, timedelta
from typing import Any

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from jose import JWTError, jwt

from rudra.core.config import get_settings

try:
    import bcrypt as _bcrypt
except ImportError:  # pragma: no cover
    _bcrypt = None


class EncryptionService:
    """AES-256 encryption for user data at rest."""

    def __init__(self, key: bytes | None = None):
        settings = get_settings()
        if key is None:
            raw = settings.rudra_encryption_key.get_secret_value().encode()
            key = base64.urlsafe_b64encode(hashlib.sha256(raw).digest())
        self._fernet = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        return self._fernet.decrypt(ciphertext.encode()).decode()

    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=600_000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))


class TokenService:
    """JWT token management for session auth."""

    def __init__(self):
        settings = get_settings()
        self._secret = settings.rudra_secret_key.get_secret_value()
        self._algorithm = settings.jwt_algorithm
        self._expire_minutes = settings.jwt_expire_minutes

    def create_token(self, subject: str, extra: dict[str, Any] | None = None) -> str:
        now = datetime.now(UTC)
        payload: dict[str, Any] = {
            "sub": subject,
            "iat": now,
            "exp": now + timedelta(minutes=self._expire_minutes),
        }
        if extra:
            payload.update(extra)
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def verify_token(self, token: str) -> dict[str, Any] | None:
        try:
            return jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except JWTError:
            return None


def hash_password(password: str) -> str:
    if _bcrypt is None:
        raise RuntimeError("bcrypt package is required for password hashing")
    return _bcrypt.hashpw(password.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    if _bcrypt is None:
        raise RuntimeError("bcrypt package is required for password hashing")
    return _bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def generate_secure_token(length: int = 32) -> str:
    return base64.urlsafe_b64encode(os.urandom(length)).decode().rstrip("=")
