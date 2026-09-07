"""Password hashing and verification using bcrypt directly."""

from __future__ import annotations

import bcrypt


def hash_password(password: str) -> str:
    """Hash a plaintext password and return the encoded string.
    
    bcrypt has a 72-byte limit on the input. We truncate to 72 bytes
    to avoid errors with very long passwords.
    """
    password_bytes = password.encode("utf-8")[:72]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a hashed password.
    
    Returns False for invalid hash formats instead of raising.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8")[:72], hashed_password.encode("utf-8")
        )
    except ValueError:
        return False
