import os
import hashlib


def encrypt_password(password: str):
    salt = os.urandom(64)
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, dklen=128)

    return salt, pw_hash


def check_password(password, salt, pw_hash):
    calculated_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, dklen=128)

    if calculated_hash == pw_hash:
        return True
    return False
