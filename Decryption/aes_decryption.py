import base64
import json
import ctypes
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


def load_raw_key_from_pem(pem_path):
    """Extract raw key from PEM file (base64 decode, remove headers)."""
    print(f"[*] Loading Kyber private key from: {pem_path}")
    with open(pem_path, 'r') as f:
        lines = f.readlines()
    key_data = ''.join(line.strip() for line in lines if not line.startswith("-----"))
    raw_key = base64.b64decode(key_data)
    print("[+] Kyber private key loaded.")
    return raw_key


def decapsulate_aes_key(encrypted_aes_key_b64, kyber_sk_path):
    print("[*] Decapsulating AES key using Kyber...")
    oqs = ctypes.CDLL("liboqs.so")

    alg = b"Kyber1024"
    oqs.OQS_KEM_new.argtypes = [ctypes.c_char_p]
    oqs.OQS_KEM_new.restype = ctypes.c_void_p
    oqs.OQS_KEM_decaps.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_ubyte),  # Shared secret (output)
        ctypes.POINTER(ctypes.c_ubyte), ctypes.c_size_t,  # Ciphertext
        ctypes.POINTER(ctypes.c_ubyte)   # Secret key
    ]
    oqs.OQS_KEM_decaps.restype = ctypes.c_int

    kem = oqs.OQS_KEM_new(alg)
    if not kem:
        raise Exception("[!] Failed to initialize Kyber KEM.")

    # Load and prepare secret key
    secret_key = load_raw_key_from_pem(kyber_sk_path)
    print(f"[DEBUG] Kyber secret key length: {len(secret_key)} bytes")
    secret_key_ct = (ctypes.c_ubyte * len(secret_key))(*secret_key)

    # Decode ciphertext
    encrypted_key_bytes = base64.b64decode(encrypted_aes_key_b64)
    print(f"[DEBUG] Encrypted AES key length: {len(encrypted_key_bytes)} bytes")
    ciphertext_ct = (ctypes.c_ubyte * len(encrypted_key_bytes))(*encrypted_key_bytes)
    # Buffer for shared secret (AES key)
    shared_secret = (ctypes.c_ubyte * 32)()

    result = oqs.OQS_KEM_decaps(
        kem,
        shared_secret,
        ciphertext_ct, len(encrypted_key_bytes),
        secret_key_ct
    )

    if result != 0:
        raise Exception("[!] Kyber decapsulation failed.")

    print("[+] AES key successfully decapsulated.")
    return bytes(shared_secret)


def decrypt_matrix(ciphertext_b64, nonce_b64, tag_b64, aes_key):
    print("[*] Decoding base64 encrypted matrix data...")
    ciphertext = base64.b64decode(ciphertext_b64)
    nonce = base64.b64decode(nonce_b64)
    tag = base64.b64decode(tag_b64)

    print("[*] Decrypting matrix using AES-GCM...")
    cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
    decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
    print("[+] Decryption successful!")
    return decrypted_data.decode('utf-8')  # assuming plaintext was UTF-8 string


def decrypt_message(msg_id):
    print(f"[*] Decrypting message with ID: {msg_id}")
    # Load encrypted data
    with open("Encrypted_data.json", "r") as file:
        encrypted_data = json.load(file)

    # Load key data
    with open("keys.json", "r") as keyfile:
        key_data = json.load(keyfile)

    if msg_id not in encrypted_data or msg_id not in key_data:
        print("[!] Message ID not found in data.")
        return

    # Extract encrypted parts
    message_data = encrypted_data[msg_id]
    encrypted_matrix = message_data["encrypted_matrix"]

    encrypted_aes_key_b64 = key_data[msg_id]["encrypted_aes_key"]
    ciphertext_b64 = encrypted_matrix["ciphertext"]
    nonce_b64 = encrypted_matrix["nonce"]
    tag_b64 = encrypted_matrix["tag"]

    # Decapsulate AES key using Kyber
    aes_key = decapsulate_aes_key(encrypted_aes_key_b64, "Encryption/key_generation/kyber_secret_key.pem")

    # Decrypt the matrix
    try:
        decrypted_plaintext = decrypt_matrix(ciphertext_b64, nonce_b64, tag_b64, aes_key)
        print("\n[+] Final Decrypted Message:")
        print(decrypted_plaintext)
    except Exception as e:
        print(f"[!] Error during decryption: {e}")


# Entry point
if __name__ == "__main__":
    msg_id = input("Enter message ID to decrypt: ").strip()
    decrypt_message(msg_id)

