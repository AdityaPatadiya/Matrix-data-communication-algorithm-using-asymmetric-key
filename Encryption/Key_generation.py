from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from main import Encryption

encryption = Encryption()

# Generate private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=3072  # You can use 3072 or 4096 for stronger security
)

# Save private key to a file
# with open("private_key.pem", "wb") as f:
#     f.write(private_key.private_bytes(
#         encoding=serialization.Encoding.PEM,
#         format=serialization.PrivateFormat.TraditionalOpenSSL,
#         encryption_algorithm=serialization.NoEncryption()
#     ))

# Generate public key
public_key = private_key.public_key()

# Save public key to a file
# with open("public_key.pem", "wb") as f:
#     f.write(public_key.public_bytes(
#         encoding=serialization.Encoding.PEM,
#         format=serialization.PublicFormat.SubjectPublicKeyInfo
#     ))

public_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

public_key_hex = encryption.hex_string(public_key)
public_key_matrix = encryption.conversion_into_matrices(public_key_hex)
print(public_key_hex)
print(public_key_matrix)

print("RSA Key Pair Generated!")
