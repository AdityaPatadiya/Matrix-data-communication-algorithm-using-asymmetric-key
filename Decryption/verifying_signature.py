import ctypes
import base64
import json
import hashlib
import binascii


class SignatureVerifier:
    """Class to verify SPHINCS+ signatures on encrypted messages."""
    def load_raw_key_from_pem(self, pem_path):
        """Extracts raw key bytes from a PEM-formatted key file."""
        with open(pem_path, 'r') as f:
            lines = f.readlines()
        key_data = ''.join(line.strip() for line in lines if not line.startswith("-----"))
        return base64.b64decode(key_data)


    def verify_signature(self, message_id):
        try:
            oqs = ctypes.CDLL("liboqs.so")
        except OSError:
            print("❌ Failed to load liboqs.so. Make sure it's installed and in your library path.")
            return

        OQS_SIG_alg_sphincs_sha2_256s_simple = b"SPHINCS+-SHA2-256s-simple"
        PUBLIC_KEY_LENGTH = 64  # For SPHINCS+-SHA2-256s-simple

        oqs.OQS_SIG_new.argtypes = [ctypes.c_char_p]
        oqs.OQS_SIG_new.restype = ctypes.c_void_p
        oqs.OQS_SIG_verify.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_ubyte)
        ]
        oqs.OQS_SIG_verify.restype = ctypes.c_int

        sig = oqs.OQS_SIG_new(OQS_SIG_alg_sphincs_sha2_256s_simple)
        if not sig:
            print("❌ Failed to initialize SPHINCS+")
            return

        try:
            public_key_bytes = self.load_raw_key_from_pem("Encryption/key_generation/sphincs_public_key.pem")
            if len(public_key_bytes) != PUBLIC_KEY_LENGTH:
                print(f"❌ Public key length mismatch. Expected {PUBLIC_KEY_LENGTH}, got {len(public_key_bytes)}")
                return
            public_key = (ctypes.c_ubyte * PUBLIC_KEY_LENGTH).from_buffer_copy(public_key_bytes)
        except FileNotFoundError:
            print("❌ Public key file not found!")
            return
        except Exception as e:
            print(f"❌ Error loading public key: {str(e)}")
            return

        try:
            with open("Encrypted_data.json", "r") as f:
                messages_db = json.load(f)
        except FileNotFoundError:
            print("❌ Messages database not found!")
            return
        except json.JSONDecodeError:
            print("❌ Invalid JSON in messages database!")
            return

        # Find the specific message by ID
        if message_id not in messages_db:
            print(f"❌ Message ID {message_id} not found in database!")
            return

        signed_payload = messages_db[message_id]

        # Decode components from Base64 with better error handling
        try:
            encrypted_data = signed_payload["encrypted_data"]
            kyber_ciphertext = base64.b64decode(encrypted_data["kyber_ciphertext"])
            aes_ciphertext = base64.b64decode(encrypted_data["aes_ciphertext"])
            nonce = base64.b64decode(encrypted_data["nonce"])
            tag = base64.b64decode(encrypted_data["tag"])
            signature = base64.b64decode(signed_payload["signature"])
        except KeyError as e:
            print(f"❌ Missing expected field in payload: {str(e)}")
            return
        except binascii.Error as e:
            print(f"❌ Base64 decoding error: {str(e)}")
            return

        # Reconstruct the signed data (must match exactly how it was signed)
        data_to_verify = kyber_ciphertext + aes_ciphertext + nonce + tag

        print("\n🔍 Verification Details:")
        print(f"Message ID: {message_id}")
        print(f"Data Length: {len(data_to_verify)} bytes")
        print(f"Data SHA256: {hashlib.sha256(data_to_verify).hexdigest()}")
        print(f"Signature Length: {len(signature)} bytes")

        # Prepare data for liboqs
        message = (ctypes.c_ubyte * len(data_to_verify))(*data_to_verify)
        signature_ct = (ctypes.c_ubyte * len(signature)).from_buffer_copy(signature)

        # Verify signature
        result = oqs.OQS_SIG_verify(
            sig,
            message, len(data_to_verify),
            signature_ct, len(signature),
            public_key
        )

        if result == 0:
            print("\n✅ SPHINCS+ Signature Verified Successfully!")
            return True
        else:
            print("\n❌ SPHINCS+ Signature Verification Failed!")
            return False
