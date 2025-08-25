from Decryption.verifying_signature import SignatureVerifier
from Decryption.aes_decryption import kyber_decrypt
from Decryption.matrix_decryption import decrypt_combined_matrix

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
                return False
            try:
                original_text = decrypt_combined_matrix(self.message_id, recover_data, "Data_utils.json")
                print(f"recovered text: {original_text}")
            except Exception as e:
                print(f"Error occur while recovering the actual data: {e}")
        else:
            print("❌ Signature verification failed. Cannot recover the data.")
            return False


if __name__ == "__main__":
    decryption = Decryption()
    decryption.decrypt()
