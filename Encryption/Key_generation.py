from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from utils import string_to_hex, conversion_into_matrices, matrix_multiplication


class Key_Generation:
    def __init__(self):
        self.private_key = ""
        self.public_key = ""
        self.public_key_matrices = []

    def private_key_generation(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=3072  # You can use 3072 or 4096 for stronger security
        )

    def public_key_generation(self):
        self.public_key = self.private_key.public_key()
        self.public_key = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def key_matrix_conversion(self):
        public_key_list = self.public_key.decode().split('\n')[2:10]
        for key_part in public_key_list:
            public_key_hex = string_to_hex(key_part)
            public_key_matrix = conversion_into_matrices(public_key_hex)
            self.public_key_matrices.append(public_key_matrix)

    def key_matrix_multiplication(self):
        key_matrix = matrix_multiplication(self.public_key_matrices)
        print(f"final key matrix: {key_matrix}")

if __name__ == "__main__":
    key_generation = Key_Generation()
    key_generation.private_key_generation()
    key_generation.public_key_generation()
    key_generation.key_matrix_conversion()
    key_generation.key_matrix_multiplication()
