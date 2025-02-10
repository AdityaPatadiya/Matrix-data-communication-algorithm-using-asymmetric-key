import numpy as np
from functools import reduce

def string_to_hex(string):
    hex_string = ''.join([hex(ord(char))[2:].zfill(2) for char in string])  # Ensure two-digit hex
    return hex_string

def conversion_into_matrices(string):
    hex_list = [string[i:i+2] for i in range(0, len(string), 2)]  # Convert hex_string into a list of single characters

    while len(hex_list) % 16 != 0:
        hex_list.append('00')  # Padding if necessary

    matrices = [
        [
            [int(hex_list[i + j + k], 16) for k in range(4)]  # Convert each hex char to int
            for j in range(0, 16, 4)
        ]
        for i in range(0, len(hex_list), 16)
    ]
    return matrices

def matrix_multiplication(matrices):
    def mat_mult(A, B):
        return (np.matmul(A, B)) % 256
    return reduce(mat_mult, matrices)