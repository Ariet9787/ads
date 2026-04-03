import hashlib
import bcrypt

_BCRYPT_ROUNDS = 12


def _sha256_hexdigest_bytes(password: str) -> bytes:
    return hashlib.sha256(password.encode()).hexdigest().encode()


def hash_password(password: str) -> str:
    prehashed = _sha256_hexdigest_bytes(password)
    salt = bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)
    return bcrypt.hashpw(prehashed, salt).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    prehashed = _sha256_hexdigest_bytes(plain_password)
    return bcrypt.checkpw(prehashed, hashed_password.encode())
