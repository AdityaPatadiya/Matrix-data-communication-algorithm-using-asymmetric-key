# from cryptography.hazmat.primitives.asymmetric import rsa
# from cryptography.hazmat.primitives import serialization
# from encryption import Encryption


# class Key_Generation:
#     def __init__(self):
#         self.private_key = ""
#         self.public_key = ""
#         self.public_key_matrices = []
#         self.enc = Encryption()

#     def private_key_generation(self):
#         self.private_key = rsa.generate_private_key(
#             public_exponent=65537,
#             key_size=3072  # You can use 3072 or 4096 for stronger security
#         )

#     def public_key_generation(self):
#         self.public_key = self.private_key.public_key()
#         self.public_key = self.public_key.public_bytes(
#             encoding=serialization.Encoding.PEM,
#             format=serialization.PublicFormat.SubjectPublicKeyInfo
#         )

#     def key_matrix_conversion(self):
#         public_key_list = self.public_key.decode().split('\n')[2:10]
#         for key_part in public_key_list:
#             public_key_hex = self.enc.string_to_hex(key_part)
#             public_key_matrix = self.enc.conversion_into_matrices(public_key_hex)
#             self.public_key_matrices.append(public_key_matrix)

#     def key_matrix_multiplication(self):
#         key_matrix = self.enc.matrix_multiplication(self.public_key_matrices)
#         print(f"final key matrix: {key_matrix}")

# if __name__ == "__main__":
#     key_generation = Key_Generation()
#     key_generation.private_key_generation()
#     key_generation.public_key_generation()
#     key_generation.key_matrix_conversion()
#     key_generation.key_matrix_multiplication()



# from pqcrypto.kem.kyber512 import generate_keypair

# # Generate Kyber public & private keys
# public_key, private_key = generate_keypair()

# with open("kyber_public_key.bin", "wb") as pub_file:
#     pub_file.write(public_key)

# with open("kyber_private_key.bin", "wb") as priv_file:
#     priv_file.write(private_key)

# print("[INFO] Kyber Key Generation Complete!")
# print(f"Public Key Length: {len(public_key)} bytes")
# print(f"Private Key Length: {len(private_key)} bytes")



from pqcrypto.kem.frodokem640shake import generate_keypair, encrypt, decrypt

# Key generation
public_key, secret_key = generate_keypair()

# Encapsulation (Bob)
ciphertext, shared_secret_bob = encrypt(public_key)

# Decapsulation (Alice)
shared_secret_alice = decrypt(ciphertext, secret_key)

# Verify shared secrets match
assert shared_secret_bob == shared_secret_alice
print("Key exchange successful!")
