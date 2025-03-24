import numpy as np
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import ctypes


def aes_encrypt(matrix):
    """Encrypts the given matrix using AES-256-GCM"""
    key = get_random_bytes(32)  # 256-bit AES key
    nonce = get_random_bytes(12)  # 12-byte nonce for GCM
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

    matrix_bytes = matrix.tobytes()  # Convert matrix to bytes
    ciphertext, tag = cipher.encrypt_and_digest(matrix_bytes)  # Encrypt and generate authentication tag

    return {
        "ciphertext": ciphertext,
        "nonce": nonce,
        "tag": tag,
        "aes_key": key
    }


def aes_decrypt(encrypted_data, key, original_shape):
    """Decrypts the AES-256-GCM encrypted data"""
    cipher = AES.new(key, AES.MODE_GCM, nonce=encrypted_data["nonce"])
    plaintext = cipher.decrypt_and_verify(encrypted_data["ciphertext"], encrypted_data["tag"])
    return np.frombuffer(plaintext, dtype=np.uint8).reshape(original_shape)


def encrypt_aes_key_with_kyber(aes_key, public_key):
    """Encrypts the AES key using Kyber for secure transmission."""
    oqs = ctypes.CDLL("liboqs.so")

    OQS_KEM_alg_kyber_1024 = b"Kyber1024"
    oqs.OQS_KEM_encaps.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte),
                                   ctypes.POINTER(ctypes.c_ubyte)]
    oqs.OQS_KEM_encaps.restype = ctypes.c_int

    kem = oqs.OQS_KEM_new(OQS_KEM_alg_kyber_1024)
    if not kem:
        raise Exception("❌ Kyber initialization failed")

    encrypted_key = (ctypes.c_ubyte * 1568)()
    shared_secret = (ctypes.c_ubyte * 32)()
    if oqs.OQS_KEM_encaps(kem, encrypted_key, shared_secret, public_key) != 0:
        raise Exception("❌ Key encapsulation failed")

    return bytes(encrypted_key)  # Return Kyber-encrypted AES key
