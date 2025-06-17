from verifying_signature import SignatureVerifier
from aes_decryption import kyber_decrypt

class Decryption:
    def __init__(self):
        self.message_id = input("Enter the message ID to decrypt: ")
        self.verify_signature = SignatureVerifier()

    def decrypt(self):
        signature_verification = self.verify_signature.verify_signature(self.message_id)
        if signature_verification == True:
            try:
                recover_data = kyber_decrypt(self.message_id)
                print(recover_data)
            except Exception as e:
                print(f"❌ Decryption failed: {str(e)}")
        else:
            print("❌ Signature verification failed. Cannot recover the data.")
            return


if __name__ == "__main__":
    decryption = Decryption()
    decryption.decrypt()
