import ctypes
import base64


class Key_Generation():
    def __init__(self) -> None:
        try:
            self.oqs = ctypes.CDLL("liboqs.so")
        except OSError as e:
            print(f"❌ Error loading liboqs: {e}")
            exit(1)

    def save_pem_file(self, filename, key_bytes, pem_type):
        """Encodes key bytes in Base64 and writes it in PEM format."""
        base64_key = base64.b64encode(key_bytes).decode('utf-8')
        pem_content = f"-----BEGIN {pem_type}-----\n"

        # Split base64 string into lines of 64 characters (PEM standard)
        pem_content += "\n".join(base64_key[i:i+64] for i in range(0, len(base64_key), 64))
        pem_content += f"\n-----END {pem_type}-----\n"

        with open(filename, "w") as f:
            f.write(pem_content)

    def kyber_key_generation(self, save_file:str):
        # Define constants
        OQS_KEM_alg_kyber_1024 = b"Kyber1024"
        PUBLIC_KEY_LENGTH = 1568
        SECRET_KEY_LENGTH = 3168

        # Ensure function signatures match expected types
        self.oqs.OQS_KEM_new.argtypes = [ctypes.c_char_p]
        self.oqs.OQS_KEM_new.restype = ctypes.c_void_p
        self.oqs.OQS_KEM_keypair.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte)]
        self.oqs.OQS_KEM_keypair.restype = ctypes.c_int

        # Initialize Kyber KEM
        kem = self.oqs.OQS_KEM_new(OQS_KEM_alg_kyber_1024)
        if not kem:
            print("❌ Failed to initialize Kyber-1024 KEM")
            exit(1)

        # Allocate memory for keys
        public_key = (ctypes.c_ubyte * PUBLIC_KEY_LENGTH)()
        secret_key = (ctypes.c_ubyte * SECRET_KEY_LENGTH)()

        # Generate keypair
        if self.oqs.OQS_KEM_keypair(kem, public_key, secret_key) != 0:
            print("❌ Key generation failed")
            exit(1)

        # Convert keys to bytes
        public_key_bytes = bytes(public_key)
        secret_key_bytes = bytes(secret_key)
        if save_file.lower() == "y":
            # Save keys in PEM format
            self.save_pem_file("Encryption/key_generation/kyber_public_key.pem", public_key_bytes, "KYBER PUBLIC KEY")
            self.save_pem_file("Encryption/key_generation/kyber_secret_key.pem", secret_key_bytes, "KYBER PRIVATE KEY")

            print("✅ Kyber-1024 Key Generation Successful!")
            print("Public Key Saved: kyber_public_key.pem")
            print("Secret Key Saved: kyber_secret_key.pem")
        else:
            print("Keys generated.")
            print(f"public key: {public_key}\nprivate key: {secret_key}")

    def generate_signature_keys(self, save_file:str):
        ALG_NAME = b"SPHINCS+-SHA2-256s-simple"
        PUBLIC_KEY_LEN = 64
        SECRET_KEY_LEN = 128

        # Function signatures
        self.oqs.OQS_SIG_new.argtypes = [ctypes.c_char_p]
        self.oqs.OQS_SIG_new.restype = ctypes.c_void_p

        self.oqs.OQS_SIG_keypair.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.POINTER(ctypes.c_ubyte),
        ]
        self.oqs.OQS_SIG_keypair.restype = ctypes.c_int

        # Create signature object
        sig = self.oqs.OQS_SIG_new(ALG_NAME)
        if not sig:
            raise Exception("Failed to initialize SPHINCS+ signer.")

        # Allocate memory for keys
        public_key = (ctypes.c_ubyte * PUBLIC_KEY_LEN)()
        private_key = (ctypes.c_ubyte * SECRET_KEY_LEN)()

        # Generate key pair
        res = self.oqs.OQS_SIG_keypair(sig, public_key, private_key)
        if res != 0:
            raise Exception("SPHINCS+ keypair generation failed.")
    
        # base64_public_key = base64.b64encode(public_key).decode('utf-8')
        # base64_private_key = base64.b64encode(private_key).decode('utf-8')

        if save_file.lower() == "y":
            self.save_pem_file("Encryption/key_generation/sphincs_public_key.pem", public_key, "PUBLIC")
            self.save_pem_file("Encryption/key_generation/sphincs_private_key.pem", private_key, "PRIVATE")
        else:
            print("keys generated.")
            print(f"public key: {public_key}\nprivate key:{private_key}")
            return public_key, private_key


# key_gnr = Key_Generation()
# key_gnr.kyber_key_generation("Y")
# key_gnr.generate_signature_keys("y")
