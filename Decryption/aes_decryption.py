import numpy as np
import base64
from Crypto.Cipher import AES
import ctypes
import json
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Encryption.key_generation.key_generation_enryption import encryption_and_decryption

enc_dec = encryption_and_decryption()

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


def encryted_data_decryption(message_id):
    """ 
    Retrieve encrypted data by messageId, 
    decapsulate AES key with Kyber, 
    and decrypt ciphertext with AES-GCM.
    """
    if not os.path.exists("Encrypted_data.json"):
        raise FileNotFoundError("❌ Encrypted_data.json not found.")
        
    with open("Encrypted_data.json", "r") as f:
        encrypted_file = json.load(f)

    if message_id not in encrypted_file:
        raise KeyError(f"❌ messageId {message_id} not found in Encrypted_data.")
        
    encrypted_data = encrypted_file[message_id]["encrypted_data"]

    # Base64-decoding first
    kyber_ciphertext = base64.b64decode(encrypted_data["kyber_ciphertext"])
    aes_ciphertext = base64.b64decode(encrypted_data["aes_ciphertext"])
    nonce = base64.b64decode(encrypted_data["nonce"])
    tag = base64.b64decode(encrypted_data["tag"])

    # Loading private key
    _, private_key = enc_dec.load_kyber_keys()
    private_key = (ctypes.c_ubyte * enc_dec.KYBER_SECRET_KEY_LENGTH).from_buffer_copy(private_key)

    # Decapsulating to retrieve AES key
    kem = oqs.OQS_KEM_new(OQS_KEM_alg_kyber_1024)
    shared_key = (ctypes.c_ubyte * 32)()
    ret = oqs.OQS_KEM_decaps(kem, shared_key, 
                             (ctypes.c_ubyte * len(kyber_ciphertext)).from_buffer_copy(kyber_ciphertext),
                             private_key)
    if ret != 0:
        raise RuntimeError("❌ Kyber decapsulation failed.")
    aes_key = bytes(shared_key)

    # AES-GCM decryption
    cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(aes_ciphertext, tag)

    return plaintext


message_id = input("Enter the message ID to decrypt: ")
encryted_data_decryption(message_id)
