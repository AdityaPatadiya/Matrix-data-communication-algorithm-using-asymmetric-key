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
        self.aes_key = b""
        self.KYBER_PUBLIC_KEY_LENGTH = 1568
        self.KYBER_SECRET_KEY_LENGTH = 3168

    def aes_encrypt(self, matrix):
        """Encrypts the given matrix using AES-256-GCM"""
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

    def load_kyber_keys(self):
        """Load the existing Kyber public and private keys and convert them to ctypes format."""

        pub_key_path = "Encryption/key_generation/kyber_public_key.pem"
        priv_key_path = "Encryption/key_generation/kyber_secret_key.pem"

        if not os.path.exists(pub_key_path) or not os.path.exists(priv_key_path):
            raise FileNotFoundError("❌ Kyber key files not found!")

        print("🔑 Loading existing Kyber key pair...")

        # Read keys as raw binary data
        with open(pub_key_path, "rb") as pub_file:
            public_key_bytes = pub_file.read()

        with open(priv_key_path, "rb") as priv_file:
            private_key_bytes = priv_file.read()

        # Convert to ctypes format
        public_key = (ctypes.c_ubyte * self.KYBER_PUBLIC_KEY_LENGTH).from_buffer_copy(public_key_bytes)
        private_key = (ctypes.c_ubyte * self.KYBER_SECRET_KEY_LENGTH).from_buffer_copy(private_key_bytes)

        print("✅ Kyber keys loaded successfully.")
        return public_key, private_key

    def kyber_encrypt(self, message_matrix, message_id):
        """Encapsulate first to generate AES key, then encrypt the message with it."""
        public_key, _ = self.load_kyber_keys()
        kem = oqs.OQS_KEM_new(OQS_KEM_alg_kyber_1024)

        ciphertext = (ctypes.c_ubyte * 1568)()
        shared_secret = (ctypes.c_ubyte * 32)()

        ret = oqs.OQS_KEM_encaps(kem, ciphertext, shared_secret, public_key)
        if ret != 0:
            raise RuntimeError("❌ Kyber encapsulation failed!")

        self.aes_key = bytes(shared_secret)

        # Now we encrypt the message_matrix with this AES key
        aes_data = self.aes_encrypt(message_matrix)

        # Prepare to store in files
        if os.path.exists("keys.json"):
            with open("keys.json", "r") as file:
                try:
                    existing_data = json.load(file)
                except json.JSONDecodeError:
                    existing_data = {}
        else:
            existing_data = {}

        existing_data[message_id] = {
            "kyber_ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
            "aes_key": base64.b64encode(shared_secret).decode('utf-8'),  # for demonstration
            "aes_ciphertext": base64.b64encode(aes_data["ciphertext"]).decode('utf-8'),
            "aes_nonce": base64.b64encode(aes_data["nonce"]).decode('utf-8'),
            "aes_tag": base64.b64encode(aes_data["tag"]).decode('utf-8'),
        }
        with open("keys.json", "w") as file:
            json.dump(existing_data, file, indent=4)

        return {
            "kyber_ciphertext": bytes(ciphertext),
            "aes_ciphertext": aes_data["ciphertext"],
            "nonce": aes_data["nonce"],
            "tag": aes_data["tag"],
        }

    def kyber_decrypt(self, kem, ciphertext, private_key):
        """Decrypt an AES key using Kyber"""
        shared_secret = (ctypes.c_ubyte * 32)()  # AES key buffer

        oqs.OQS_KEM_decaps(kem, shared_secret, ciphertext, private_key)

        return bytes(shared_secret)  # Returns the original AES key
