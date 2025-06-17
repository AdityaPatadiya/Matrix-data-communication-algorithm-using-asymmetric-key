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


class encryption:
    def __init__(self):
        self.aes_key = b""
        self.KYBER_PUBLIC_KEY_LENGTH = 1568
        self.KYBER_SECRET_KEY_LENGTH = 3168

    def aes_encrypt(self, matrix):
        """Encrypts the given matrix using AES-256-GCM"""
        nonce = get_random_bytes(12)  # 12-byte nonce for GCM
        cipher = AES.new(self.aes_key, AES.MODE_GCM, nonce=nonce)
        if isinstance(matrix, np.ndarray):
            matrix_as_list = matrix.tolist()
        else:
            matrix_as_list = matrix

        json_string = json.dumps(matrix_as_list)

        bytes_data = json_string.encode('utf-8')
        ciphertext, tag = cipher.encrypt_and_digest(bytes_data)  # Encrypt and generate authentication tag

        return {
            "ciphertext": ciphertext,
            "nonce": nonce,
            "tag": tag,
            "aes_key": self.aes_key
        }

    def load_raw_key_from_pem(self, pem_path):
        """Extracts raw key bytes from a PEM-formatted key file."""
        with open(pem_path, 'rb') as f:
            data = f.read()
        # Extract base64 payload between headers
        start_tag = b"-----BEGIN "
        end_tag = b"-----END "
        start_idx = data.find(b"\n", data.find(start_tag)) + 1
        end_idx = data.rfind(end_tag, start_idx)
        key_data = b"".join(data[start_idx:end_idx].splitlines())
        return base64.b64decode(key_data)

    def load_kyber_keys(self):
        """Properly load PEM-formatted keys"""
        pub_key_path = "Encryption/key_generation/kyber_public_key.pem"
        priv_key_path = "Encryption/key_generation/kyber_secret_key.pem"

        if not os.path.exists(pub_key_path) or not os.path.exists(priv_key_path):
            raise FileNotFoundError("❌ Kyber key files not found!")

        public_key_bytes = self.load_raw_key_from_pem(pub_key_path)
        private_key_bytes = self.load_raw_key_from_pem(priv_key_path)

        # Convert to ctypes
        public_key = (ctypes.c_ubyte * self.KYBER_PUBLIC_KEY_LENGTH).from_buffer_copy(public_key_bytes)
        private_key = (ctypes.c_ubyte * self.KYBER_SECRET_KEY_LENGTH).from_buffer_copy(private_key_bytes)

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
