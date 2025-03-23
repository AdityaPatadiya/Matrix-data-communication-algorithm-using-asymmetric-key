import ctypes

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

# Save keys to files
with open("kyber_public_key.bin", "wb") as f:
    f.write(public_key_bytes)

with open("kyber_secret_key.bin", "wb") as f:
    f.write(secret_key_bytes)

print("✅ Kyber-1024 Key Generation Successful!")
print(f"Public Key Saved: kyber_public_key.bin ({len(public_key_bytes)} bytes)")
print(f"Secret Key Saved: kyber_secret_key.bin ({len(secret_key_bytes)} bytes)")


# import ctypes
# import base64

# # Load the liboqs shared library
# liboqs = ctypes.CDLL("liboqs.so")

# # Define constants
# KYBER_ALG = b"OQS_KEM_alg_kyber_1024"
# PUBLIC_KEY_SIZE = 1568   # Kyber1024 public key size
# SECRET_KEY_SIZE = 3168   # Kyber1024 private key size

# # Function prototypes
# liboqs.OQS_KEM_new.restype = ctypes.c_void_p
# liboqs.OQS_KEM_keypair.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte)]

# # Initialize Kyber algorithm
# kem = liboqs.OQS_KEM_new(KYBER_ALG)

# # Allocate memory for keys
# public_key = (ctypes.c_ubyte * PUBLIC_KEY_SIZE)()
# secret_key = (ctypes.c_ubyte * SECRET_KEY_SIZE)()

# # Generate key pair
# liboqs.OQS_KEM_keypair(kem, public_key, secret_key)

# # Convert to bytes
# public_key_bytes = bytes(public_key)
# secret_key_bytes = bytes(secret_key)

# def save_pem(filename, key_data, key_type):
#     """Save key in a PEM-like format"""
#     encoded_key = base64.b64encode(key_data).decode('utf-8')
#     pem_content = f"-----BEGIN {key_type} KEY-----\n"
#     pem_content += "\n".join(encoded_key[i:i+64] for i in range(0, len(encoded_key), 64))  # Format in 64-char lines
#     pem_content += f"\n-----END {key_type} KEY-----\n"

#     with open(filename, "w") as f:
#         f.write(pem_content)

# # Save keys to files
# save_pem("public_key.pem", public_key_bytes, "KYBER PUBLIC")
# save_pem("secret_key.pem", secret_key_bytes, "KYBER PRIVATE")

# print("✅ Kyber-1024 Key Pair Generated & Saved as PEM")


# import ctypes
# import base64
# import os

# # Load liboqs
# oqs = ctypes.cdll.LoadLibrary("/usr/local/lib/liboqs.so")

# # Define function prototypes for key generation
# oqs.oqs_kem_new.restype = ctypes.c_void_p
# oqs.oqs_kem_free.argtypes = [ctypes.c_void_p]
# oqs.oqs_kem_keypair.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]

# # Kyber variant (change to "OQS_KEM_alg_kyber768" if needed)
# kyber_algorithm = b"OQS_KEM_alg_kyber1024"

# # Initialize Kyber KEM
# kem = oqs.oqs_kem_new(kyber_algorithm)
# if not kem:
#     raise RuntimeError("Failed to initialize Kyber KEM")

# # Allocate memory for public and private keys
# public_key = ctypes.create_string_buffer(1568)  # Adjust size as per Kyber variant
# secret_key = ctypes.create_string_buffer(3168)  # Adjust size as per Kyber variant

# # Generate Keypair
# if oqs.oqs_kem_keypair(kem, public_key, secret_key) != 0:
#     raise RuntimeError("Kyber key generation failed")

# # Free KEM
# oqs.oqs_kem_free(kem)

# # Function to write keys in Base64-encoded PEM-like format
# def write_key_to_pem(key_data, filename, key_type):
#     encoded_key = base64.b64encode(key_data.raw).decode("utf-8")
#     with open(filename, "w") as f:
#         f.write(f"-----BEGIN KYBER {key_type} KEY-----\n")
#         for i in range(0, len(encoded_key), 64):
#             f.write(encoded_key[i:i+64] + "\n")
#         f.write(f"-----END KYBER {key_type} KEY-----\n")

# # Write keys to PEM files
# write_key_to_pem(public_key, "public_key.pem", "PUBLIC")
# write_key_to_pem(secret_key, "secret_key.pem", "PRIVATE")

# print("Kyber Key Pair Generated Successfully!")
# print("Public Key saved to 'public_key.pem'")
# print("Private Key saved to 'secret_key.pem'")

