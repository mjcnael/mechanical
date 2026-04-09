from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, password_hash_value: str | None) -> bool:
    if not password_hash_value:
        return False
    return password_hash.verify(password, password_hash_value)
