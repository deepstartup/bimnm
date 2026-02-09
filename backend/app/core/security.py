"""JWT and password hashing."""
import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from app.config import settings

# Use SHA256 with salt to avoid bcrypt 72-byte limit and passlib/bcrypt version issues.
# Format in DB: "sha256$<hex(salt)>$<hex(hash)>"
def get_password_hash(password: str) -> str:
    salt = os.urandom(32)
    h = hashlib.sha256(salt + password.encode("utf-8")).hexdigest()
    return f"sha256${salt.hex()}${h}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password or not hashed_password.startswith("sha256$"):
        return False
    parts = hashed_password.split("$", 2)
    if len(parts) != 3:
        return False
    _, salt_hex, stored_hex = parts
    salt = bytes.fromhex(salt_hex)
    h = hashlib.sha256(salt + plain_password.encode("utf-8")).hexdigest()
    return h == stored_hex


def create_access_token(subject: str | int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload.get("sub")
    except JWTError:
        return None
