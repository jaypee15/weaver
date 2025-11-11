"""Authentication utility functions"""
import secrets
from passlib.hash import argon2


def generate_api_key() -> str:
    """Generate a new API key with 'wvr_' prefix"""
    return f"wvr_{secrets.token_urlsafe(48)}"


def hash_api_key(key: str) -> str:
    """Hash an API key using Argon2"""
    return argon2.hash(key)


def verify_key_hash(key: str, key_hash: str) -> bool:
    """Verify an API key against its hash"""
    try:
        return argon2.verify(key, key_hash)
    except Exception:
        return False

