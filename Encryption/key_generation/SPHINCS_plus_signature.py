import ctypes
import base64
import numpy as np
import hashlib

def add_signature(encrypted_data):
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
        def load_raw_key_from_pem(pem_path):
            """Extracts raw key bytes from a PEM-formatted key file."""
            with open(pem_path, 'r') as f:
                lines = f.readlines()
            key_data = ''.join(line.strip() for line in lines if not line.startswith("-----"))
            return base64.b64decode(key_data)

        # Now use it to load keys correctly
        public_key_bytes = load_raw_key_from_pem("Encryption/key_generation/sphincs_public_key.pem")
        secret_key_bytes = load_raw_key_from_pem("Encryption/key_generation/sphincs_private_key.pem")
    except FileNotFoundError:
        print("❌ Key files not found! Generate keys first.")
        exit(1)

    # Convert keys to ctypes format
    public_key = (ctypes.c_ubyte * PUBLIC_KEY_LENGTH).from_buffer_copy(public_key_bytes)
    secret_key = (ctypes.c_ubyte * SECRET_KEY_LENGTH).from_buffer_copy(secret_key_bytes)

    # 👉 Combine ciphertext + nonce + tag to sign
    data_to_sign = encrypted_data["kyber_ciphertext"] + encrypted_data["aes_ciphertext"] + encrypted_data["nonce"] + encrypted_data["tag"]

    # Allocate memory for signature
    signature = (ctypes.c_ubyte * SIGNATURE_LENGTH)()
    signature_len = ctypes.c_size_t()

    print("🔐 Signing Data Length:", len(data_to_sign))
    print("🔐 Signing Data SHA256:", hashlib.sha256(data_to_sign).hexdigest())

    # Sign the matrix (data)
    if oqs.OQS_SIG_sign(sig, signature, ctypes.byref(signature_len),
                        (ctypes.c_ubyte * len(data_to_sign))(*data_to_sign), len(data_to_sign), secret_key) != 0:
        print("❌ Signing failed")
        exit(1)

    # 👉 Return the signed payload instead of NumPy concat
    signed_payload = {
        "encrypted_data": {
            "kyber_ciphertext": base64.b64encode(encrypted_data["kyber_ciphertext"]).decode('utf-8'),
            "aes_ciphertext": base64.b64encode(encrypted_data["aes_ciphertext"]).decode('utf-8'),
            "nonce": base64.b64encode(encrypted_data["nonce"]).decode('utf-8'),
            "tag": base64.b64encode(encrypted_data["tag"]).decode('utf-8'),
        },
        "signature": base64.b64encode(bytes(signature[:signature_len.value])).decode('utf-8')
    }

    print("\n✅ SPHINCS+ Signature Generated and Attached!")
    return signed_payload
