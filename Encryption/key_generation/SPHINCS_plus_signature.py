import ctypes
import numpy as np

def add_signature(matrix):
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

    # convert keys to ctypes format
    public_key = (ctypes.c_ubyte * PUBLIC_KEY_LENGTH).from_buffer_copy(public_key_bytes)
    secret_key = (ctypes.c_ubyte * SECRET_KEY_LENGTH).from_buffer_copy(secret_key_bytes)

    # Assume final_matrix is your last matrix (Example: 4x4)
    final_matrix = matrix  # Replace with your real matrix

    # Convert matrix to bytes
    matrix_bytes = final_matrix.tobytes()

    # Allocate memory for signature
    signature = (ctypes.c_ubyte * SIGNATURE_LENGTH)()
    signature_len = ctypes.c_size_t()

    # Sign the matrix
    if oqs.OQS_SIG_sign(sig, signature, ctypes.byref(signature_len),
                        (ctypes.c_ubyte * len(matrix_bytes))(*matrix_bytes), len(matrix_bytes), secret_key) != 0:
        print("❌ Signing failed")
        exit(1)

    # Append the signature to the matrix
    signed_matrix = np.concatenate((final_matrix.flatten(), np.frombuffer(signature, dtype=np.uint8)))

    # Reshape to store as a single-row matrix (if needed)
    signed_matrix = signed_matrix.reshape(1, -1)  # 1 row, many columns

    print("\n✅ SPHINCS+ Signature Generated and Appended!")
    print(f"Signed Matrix Shape: {signed_matrix.shape}")

    np.set_printoptions(threshold=np.inf)
    return signed_matrix
