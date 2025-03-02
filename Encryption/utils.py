import numpy as np
from functools import reduce
import math

MATRIX_SIZES = [2, 3, 4, 6]

def string_to_hex(string):
    """Convert a string into hex representation."""
    hex_string = ''.join([hex(ord(char))[2:].zfill(2) for char in string])
    return hex_string

def choose_matrix_size(data_length):
    """Choose the largest matrix size that can be consistently used."""
    for size in reversed(MATRIX_SIZES):
        if data_length >= size**2:
            return size
    return 2

def apply_pkcs7_padding(hex_list, block_size):
    """Apply PKCS#7 padding so that the block is a perfect square matrix."""
    padding_needed = block_size**2 - len(hex_list)
    padding_value = hex(padding_needed)[2:].zfill(2)  # PKCS#7 padding
    hex_list.extend([padding_value] * padding_needed)
    return hex_list

def split_blocks(hex_list, block_size):
    """Split hex data into consistent-sized matrices."""
    blocks = []
    i = 0
    while i < len(hex_list):
        block = hex_list[i:i + block_size**2]
        if len(block) < block_size**2:
            block = apply_pkcs7_padding(block, block_size)
        blocks.append(block)
        i += block_size**2
    return blocks

def conversion_into_matrices(hex_list):
    """Convert hex blocks into square matrices of uniform size."""
    matrix_size = choose_matrix_size(len(hex_list))  # Choose a fixed size
    blocks = split_blocks(hex_list, matrix_size)
    matrices = []

    for block in blocks:
        matrix = np.array([
            [int(block[i + j], 16) for j in range(matrix_size)]
            for i in range(0, len(block), matrix_size)
        ])
        matrices.append(matrix)

    return matrices

def matrix_multiplication(matrices):
    """Perform chained matrix multiplication with proper dimensions."""
    if len(matrices) == 1:
        return matrices[0]

    def mat_mult(A, B):
        print(f"\nMultiplying Matrices:\n{A}\nAND\n{B}")
        return np.mod(np.matmul(A, B), 256)

    return reduce(mat_mult, matrices)

plaintext = "Hello"
hex_string = string_to_hex(plaintext)
hex_list = [hex_string[i:i+2] for i in range(0, len(hex_string), 2)]
print(f"hex_list: {hex_list}")

matrices = conversion_into_matrices(hex_list)
result_matrix = matrix_multiplication(matrices)

print("\nHex String:", hex_string)
print("\nGenerated Matrices:")
for matrix in matrices:
    print(matrix)
print("\nResultant Matrix:\n", result_matrix)
