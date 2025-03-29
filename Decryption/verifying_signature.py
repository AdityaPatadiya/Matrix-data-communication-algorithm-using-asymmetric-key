import ctypes
import base64
import json

# Load SPHINCS+ shared library
sphincs_lib = ctypes.CDLL("./libsphincs.so")  # Ensure this path is correct

# SPHINCS+ Signature and Public Key Lengths
SIGNATURE_LENGTH = 29792  # Adjust based on SPHINCS+ variant
PUBLIC_KEY_LENGTH = 64  # Adjust based on your key type

def verify_sphincs_signature(signed_message):
    """Verify the SPHINCS+ signature using ctypes."""

    # Ensure signed_message is in bytes
    if isinstance(signed_message, str):
        signed_message = base64.b64decode(signed_message)  # Decode if it's a base64 string

    # Extract the last SIGNATURE_LENGTH bytes as the signature
    signature = signed_message[-SIGNATURE_LENGTH:]
    message = signed_message[:-SIGNATURE_LENGTH]

    # Read SPHINCS+ public key
    with open("Encryption/key_generation/sphincs_public_key.pem", 'rb') as pub_file:
        public_key = pub_file.read()

    # Convert data to ctypes
    c_message = (ctypes.c_ubyte * len(message)).from_buffer_copy(message)
    c_signature = (ctypes.c_ubyte * SIGNATURE_LENGTH).from_buffer_copy(signature)
    c_public_key = (ctypes.c_ubyte * PUBLIC_KEY_LENGTH).from_buffer_copy(public_key)

    # Call the SPHINCS+ verification function from the C library
    verify_func = sphincs_lib.sphincs_verify
    verify_func.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_size_t,
                            ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte)]
    verify_func.restype = ctypes.c_int

    # Perform verification
    result = verify_func(c_message, len(message), c_signature, c_public_key)

    if result == 1:
        print("✅ Signature verification successful! Message is authentic.")
        return message  # Return the extracted message for decryption
    else:
        raise ValueError("❌ Signature verification failed! Message may be tampered with.")

# Read the signed message from the encrypted data file
with open("Encrypted_data.json", 'r') as file:
    data = json.load(file)

# Assuming the message is stored under a message ID and is base64-encoded
message_id = list(data.keys())[0]  # Get first message ID
signed_message = data[message_id]["final_ciphertext"]  # Adjust key name if needed

# Verify the signature
try:
    extracted_message = verify_sphincs_signature(signed_message)
    print("Extracted Message (After Signature Verification):", extracted_message)
except ValueError as e:
    print(e)
