import ctypes
import base64

# Load the liboqs shared library
try:
    oqs = ctypes.CDLL("liboqs.so")
except OSError as e:
    print(f"❌ Error loading liboqs: {e}")
    exit(1)

# Define constants
OQS_KEM_alg_kyber_1024 = b"Kyber1024"
PUBLIC_KEY_LENGTH = 1568
SECRET_KEY_LENGTH = 3168

# Ensure function signatures match expected types
oqs.OQS_KEM_new.argtypes = [ctypes.c_char_p]
oqs.OQS_KEM_new.restype = ctypes.c_void_p
oqs.OQS_KEM_keypair.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte)]
oqs.OQS_KEM_keypair.restype = ctypes.c_int

# Initialize Kyber KEM
kem = oqs.OQS_KEM_new(OQS_KEM_alg_kyber_1024)
if not kem:
    print("❌ Failed to initialize Kyber-1024 KEM")
    exit(1)

# Allocate memory for keys
public_key = (ctypes.c_ubyte * PUBLIC_KEY_LENGTH)()
secret_key = (ctypes.c_ubyte * SECRET_KEY_LENGTH)()

# Generate keypair
if oqs.OQS_KEM_keypair(kem, public_key, secret_key) != 0:
    print("❌ Key generation failed")
    exit(1)

# Convert keys to bytes
public_key_bytes = bytes(public_key)
secret_key_bytes = bytes(secret_key)

# Convert to Base64 and format as PEM
def save_pem_file(filename, key_bytes, pem_type):
    """Encodes key bytes in Base64 and writes it in PEM format."""
    base64_key = base64.b64encode(key_bytes).decode('utf-8')
    pem_content = f"-----BEGIN {pem_type}-----\n"

    # Split base64 string into lines of 64 characters (PEM standard)
    pem_content += "\n".join(base64_key[i:i+64] for i in range(0, len(base64_key), 64))
    pem_content += f"\n-----END {pem_type}-----\n"

    with open(filename, "w") as f:
        f.write(pem_content)

# Save keys in PEM format
save_pem_file("kyber_public_key.pem", public_key_bytes, "KYBER PUBLIC KEY")
save_pem_file("kyber_secret_key.pem", secret_key_bytes, "KYBER PRIVATE KEY")

print("✅ Kyber-1024 Key Generation Successful!")
print("Public Key Saved: kyber_public_key.pem")
print("Secret Key Saved: kyber_secret_key.pem")
