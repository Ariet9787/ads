import hashlib
import bcrypt

_BCRYPT_ROUNDS = 12


def _sha256_hexdigest_bytes(password: str) -> bytes:
    return hashlib.sha256(password.encode()).hexdigest().encode()


def get_password_hash(password: str) -> str:
    prehashed = _sha256_hexdigest_bytes(password)
    salt = bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(prehashed, salt)
    return hashed.decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    hp_bytes = hashed_password.encode()

    prehashed = _sha256_hexdigest_bytes(plain_password)
    if bcrypt.checkpw(prehashed, hp_bytes):
        return True

    try:
        return bcrypt.checkpw(plain_password.encode(), hp_bytes)
    except ValueError:
        return False
