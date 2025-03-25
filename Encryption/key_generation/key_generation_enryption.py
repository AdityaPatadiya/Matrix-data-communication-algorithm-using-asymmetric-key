import numpy as np
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import ctypes
import json
import os


oqs = ctypes.CDLL("liboqs.so")

OQS_KEM_alg_kyber_1024 = b"Kyber1024"

# Function prototypes
oqs.OQS_KEM_new.argtypes = [ctypes.c_char_p]
oqs.OQS_KEM_new.restype = ctypes.c_void_p

oqs.OQS_KEM_keypair.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte)]
oqs.OQS_KEM_keypair.restype = ctypes.c_int

oqs.OQS_KEM_encaps.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte),
                               ctypes.POINTER(ctypes.c_ubyte)]
oqs.OQS_KEM_encaps.restype = ctypes.c_int

oqs.OQS_KEM_decaps.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte),
                               ctypes.POINTER(ctypes.c_ubyte)]
oqs.OQS_KEM_decaps.restype = ctypes.c_int


class encryption_and_decryption:
    def __init__(self):
        self.aes_key = ""

    def aes_encrypt(self, matrix):
        """Encrypts the given matrix using AES-256-GCM"""
        self.aes_key = get_random_bytes(32)  # 256-bit AES key
        nonce = get_random_bytes(12)  # 12-byte nonce for GCM
        cipher = AES.new(self.aes_key, AES.MODE_GCM, nonce=nonce)

        matrix_bytes = matrix.tobytes()  # Convert matrix to bytes
        ciphertext, tag = cipher.encrypt_and_digest(matrix_bytes)  # Encrypt and generate authentication tag

        return {
            "ciphertext": ciphertext,
            "nonce": nonce,
            "tag": tag,
            "aes_key": self.aes_key
        }


    def aes_decrypt(self, encrypted_data, key, original_shape):
        """Decrypts the AES-256-GCM encrypted data"""
        cipher = AES.new(key, AES.MODE_GCM, nonce=encrypted_data["nonce"])
        plaintext = cipher.decrypt_and_verify(encrypted_data["ciphertext"], encrypted_data["tag"])
        return np.frombuffer(plaintext, dtype=np.uint8).reshape(original_shape)


    def generate_kyber_keypair(self, message_id):
        """Generate a Kyber keypair and encrypt the AES key"""
        kem = oqs.OQS_KEM_new(OQS_KEM_alg_kyber_1024)

        public_key = (ctypes.c_ubyte * 1568)()
        private_key = (ctypes.c_ubyte * 3168)()

        status = oqs.OQS_KEM_keypair(kem, public_key, private_key)
        if status != 0:
            raise RuntimeError("Failed to generate Kyber keypair")

        public_key_encoded = base64.b64encode(bytes(public_key)).decode('utf-8')
        private_key_encoded = base64.b64encode(bytes(private_key)).decode('utf-8')

        ciphertext, encrypted_aes_key = self.kyber_encrypt(kem, public_key, self.aes_key)

        if os.path.exists("keys.json"):
            with open("keys.json", 'r') as file:
                try:
                    existing_data = json.load(file)
                except json.JSONDecodeError:
                    existing_data = {}
        else:
            existing_data = {}

        existing_data[message_id] = {
            "public_key": public_key_encoded,
            "private_key": private_key_encoded,
            "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
            "encrypted_aes_key": base64.b64encode(encrypted_aes_key).decode('utf-8')
        }

        with open("keys.json", 'w') as file:
            json.dump(existing_data, file, indent=4)

        return ciphertext, encrypted_aes_key


    def kyber_encrypt(self, kem, public_key, aes_key):
        """Encrypt an AES key using Kyber"""
        ciphertext = (ctypes.c_ubyte * 1568)()  # Kyber ciphertext size
        shared_secret = (ctypes.c_ubyte * 32).from_buffer_copy(aes_key)  # AES key

        oqs.OQS_KEM_encaps(kem, ciphertext, shared_secret, public_key)

        return bytes(ciphertext), bytes(shared_secret)  # `shared_secret` is the AES key

    def kyber_decrypt(self, kem, ciphertext, private_key):
        """Decrypt an AES key using Kyber"""
        shared_secret = (ctypes.c_ubyte * 32)()  # AES key buffer

        oqs.OQS_KEM_decaps(kem, shared_secret, ciphertext, private_key)

        return bytes(shared_secret)  # Returns the original AES key
