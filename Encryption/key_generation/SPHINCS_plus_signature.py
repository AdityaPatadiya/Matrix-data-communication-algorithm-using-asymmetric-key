import ctypes
import base64
import numpy as np

def add_signature(encrypted_matrix):
    # Load liboqs
    oqs = ctypes.CDLL("liboqs.so")

    # SPHINCS+ Constants
    OQS_SIG_alg_sphincs_sha2_256s_simple = b"SPHINCS+-SHA2-256s-simple"
    SIGNATURE_LENGTH = 29792  # SPHINCS+-SHA2-256s-simple signature length
    PUBLIC_KEY_LENGTH = 64
    SECRET_KEY_LENGTH = 128

    # Function Prototypes
    oqs.OQS_SIG_new.argtypes = [ctypes.c_char_p]
    oqs.OQS_SIG_new.restype = ctypes.c_void_p
    oqs.OQS_SIG_keypair.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte)]
    oqs.OQS_SIG_keypair.restype = ctypes.c_int
    oqs.OQS_SIG_sign.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_size_t),
                                 ctypes.POINTER(ctypes.c_ubyte), ctypes.c_size_t, ctypes.POINTER(ctypes.c_ubyte)]
    oqs.OQS_SIG_sign.restype = ctypes.c_int

    # Initialize SPHINCS+
    sig = oqs.OQS_SIG_new(OQS_SIG_alg_sphincs_sha2_256s_simple)
    if not sig:
        print("❌ Failed to initialize SPHINCS+")
        exit(1)

    # Load Public and Private Keys from Files
    try:
        with open("Encryption/key_generation/sphincs_public_key.pem", "rb") as pub_file:
            public_key_bytes = pub_file.read()

        with open("Encryption/key_generation/sphincs_private_key.pem", "rb") as priv_file:
            secret_key_bytes = priv_file.read()
    except FileNotFoundError:
        print("❌ Key files not found! Generate keys first.")
        exit(1)

    # Convert keys to ctypes format
    public_key = (ctypes.c_ubyte * PUBLIC_KEY_LENGTH).from_buffer_copy(public_key_bytes)
    secret_key = (ctypes.c_ubyte * SECRET_KEY_LENGTH).from_buffer_copy(secret_key_bytes)

    # 👉 Combine ciphertext + nonce + tag to sign
    data_to_sign = encrypted_matrix["ciphertext"] + encrypted_matrix["nonce"] + encrypted_matrix["tag"]

    # Allocate memory for signature
    signature = (ctypes.c_ubyte * SIGNATURE_LENGTH)()
    signature_len = ctypes.c_size_t()

    # Sign the matrix (data)
    if oqs.OQS_SIG_sign(sig, signature, ctypes.byref(signature_len),
                        (ctypes.c_ubyte * len(data_to_sign))(*data_to_sign), len(data_to_sign), secret_key) != 0:
        print("❌ Signing failed")
        exit(1)

    # 👉 Return the signed payload instead of NumPy concat
    signed_payload = {
        "encrypted_matrix": {
            "ciphertext": base64.b64encode(encrypted_matrix["ciphertext"]).decode('utf-8'),
            "nonce": base64.b64encode(encrypted_matrix["nonce"]).decode('utf-8'),
            "tag": base64.b64encode(encrypted_matrix["tag"]).decode('utf-8')
        },
        "signature": bytes(signature[:signature_len.value]).hex()
    }

    print("\n✅ SPHINCS+ Signature Generated and Attached!")
    return signed_payload
