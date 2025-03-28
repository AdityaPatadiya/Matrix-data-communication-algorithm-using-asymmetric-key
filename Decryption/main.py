import json
import numpy as np
import ctypes

def load_message_data(message_id, filename="data.json"):
    """Load matrix and signature data for the given message_id"""
    try:
        with open(filename, 'r') as file:
            data = json.load(file)

        if message_id not in data:
            print("❌ Message ID not found!")
            return None, None, None

        message_data = data[message_id]

        # Extract stored data
        matrix_data = np.array(message_data[:-SIGNATURE_LENGTH], dtype=np.uint8)  # Matrix
        signature = np.array(message_data[-SIGNATURE_LENGTH:], dtype=np.uint8)  # Signature

        return matrix_data, signature, message_id

    except Exception as e:
        print(f"Error loading message data: {e}")
        return None, None, None


# Load liboqs
oqs = ctypes.CDLL("liboqs.so")

# SPHINCS+ Constants
OQS_SIG_alg_sphincs_sha2_256s_simple = b"SPHINCS+-SHA2-256s-simple"
SIGNATURE_LENGTH = 29792  # SPHINCS+-SHA2-256s-simple signature length
PUBLIC_KEY_LENGTH = 64

# Initialize SPHINCS+
oqs.OQS_SIG_new.argtypes = [ctypes.c_char_p]
oqs.OQS_SIG_new.restype = ctypes.c_void_p
oqs.OQS_SIG_verify.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_size_t,
                               ctypes.POINTER(ctypes.c_ubyte), ctypes.c_size_t,
                               ctypes.POINTER(ctypes.c_ubyte)]
oqs.OQS_SIG_verify.restype = ctypes.c_int

def verify_signature(matrix_data, signature, public_key):
    """Verify the SPHINCS+ signature"""
    sig = oqs.OQS_SIG_new(OQS_SIG_alg_sphincs_sha2_256s_simple)
    if not sig:
        print("❌ Failed to initialize SPHINCS+")
        return False

    matrix_bytes = matrix_data.tobytes()

    # Verify the signature
    status = oqs.OQS_SIG_verify(sig,
                                signature.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)), SIGNATURE_LENGTH,
                                (ctypes.c_ubyte * len(matrix_bytes))(*matrix_bytes), len(matrix_bytes),
                                public_key)

    if status == 0:
        print("✅ Signature Verified Successfully!")
        return True
    else:
        print("❌ Signature Verification Failed!")
        return False

def process_verification(message_id, public_key):
    """Retrieve message and verify SPHINCS+ signature"""
    matrix_data, signature, msg_id = load_message_data(message_id)

    if matrix_data is None or signature is None:
        return False

    # Verify signature
    return verify_signature(matrix_data, signature, public_key)

message_id = "a92224f7f1f186f5e987dfe20da3171adccc41732848ba85c3fbbac76caec940"
public_key = ...  # Load the SPHINCS+ public key from storage

if process_verification(message_id, public_key):
    print("Message is authentic. Proceeding with decryption.")
else:
    print("Message verification failed. Do not decrypt!")
