import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import shutil
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256
import base64



def generate_key(password: str,  salt: bytes) -> bytes:
    # Derive a secure key from the password
    return derive_key(password, salt)  # Replace with a secure key derivation function

# Encrypt a file
def encrypt_file(key: bytes, file_path: str):
    cipher = Fernet(key)
    with open(file_path, "rb") as file:
        data = file.read()
    encrypted_data = cipher.encrypt(data)
    with open(file_path, "wb") as file:
        file.write(encrypted_data)

# Decrypt a file
def decrypt_file(key: bytes, file_path: str):
    cipher = Fernet(key)
    with open(file_path, "rb") as file:
        encrypted_data = file.read()
    decrypted_data = cipher.decrypt(encrypted_data)
    with open(file_path, "wb") as file:
        file.write(decrypted_data)

def encrypt_folder(key: bytes, folder_path: str):
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            encrypt_file(key, file_path)

# Decrypt all files in a folder
def decrypt_folder(key: bytes, folder_path: str, temp_folder: str):
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
    shutil.copytree(folder_path, temp_folder)
    for root, _, files in os.walk(temp_folder):
        for file in files:
            file_path = os.path.join(root, file)
            decrypt_file(key, file_path)


# Hash the password
def hash_password(password: str, salt: bytes) -> (bytes, bytes):
    # Generate a salt (16 bytes)
    # salt = os.urandom(16)

    # PBKDF2-HMAC using SHA256
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 32-byte output (256-bit)
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )

    # Generate the hash
    hashed_password = kdf.derive(password.encode())

    return hashed_password

def derive_key(password: str, salt: bytes, iterations: int = 100_000, key_length: int = 32) -> bytes:
    """
    Derives a secure encryption key from a password using PBKDF2-HMAC-SHA256.

    :param password: The password string to derive the key from.
    :param salt: A randomly generated salt (16-32 bytes recommended).
    :param iterations: Number of iterations for the key derivation (default: 100,000).
    :param key_length: Length of the derived key in bytes (default: 32 for AES-256).
    :return: A securely derived encryption key.
    """
    kdf = PBKDF2HMAC(
        algorithm=SHA256(),
        length=key_length,
        salt=salt,
        iterations=iterations,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def generate_salt(length: int = 16) -> bytes:
    """
    Generates a cryptographically secure random salt.

    :param length: Length of the salt in bytes (default: 16).
    :return: A random salt.
    """
    return os.urandom(length)


def verify_password(password: str, derived_key: bytes, salt: bytes, iterations: int = 100_000,
                    key_length: int = 32) -> bool:
    """
    Verifies if a password matches the derived key using the same salt and iterations.

    :param password: The password string to verify.
    :param derived_key: The previously derived key.
    :param salt: The salt used for deriving the key.
    :param iterations: Number of iterations for the key derivation.
    :param key_length: Length of the derived key in bytes.
    :return: True if the password matches, False otherwise.
    """
    try:
        kdf = PBKDF2HMAC(
            algorithm=SHA256(),
            length=key_length,
            salt=salt,
            iterations=iterations,
        )
        kdf.verify(password.encode(), derived_key)
        return True
    except Exception:
        return False