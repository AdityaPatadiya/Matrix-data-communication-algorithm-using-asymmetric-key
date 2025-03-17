import numpy as np
import random
from functools import reduce

from utils import apply_random_operations


class Encryption:
    def __init__(self):
        self.hex_string = ""
        self.matrices = []
        self.MATRIX_SIZES = [2, 3, 4, 6]
        self.operation_sequences = []

    def string_to_hex(self, string):
        """Convert a string into hex representation."""
        hex_string = ''.join([hex(ord(char))[2:].zfill(2) for char in string])
        print(f"hex string: {hex_string}\n")
        return hex_string

    def choose_matrix_size(self, data_length):
        """Choose the largest matrix size that can be consistently used."""
        for size in reversed(self.MATRIX_SIZES):
            if data_length >= size**2:
                return size
        return 2

    def apply_random_padding(self, hex_list, block_size):
        """Apply randomized padding to ensure block is a perfect square matrix."""
        padding_needed = block_size**2 - len(hex_list)

        if padding_needed > 0:
            # Generate random hex values instead of deterministic ones
            random_padding = [hex(random.randint(0, 255))[2:].zfill(2) for _ in range(padding_needed)]
            hex_list.extend(random_padding)

        print(f"Random padding applied: {random_padding}\n")
        print(f"hex_list: {hex_list}")
        return hex_list

    def split_blocks(self, hex_list, block_size):
        """Split hex data into consistent-sized matrices."""
        blocks = []
        i = 0
        while i < len(hex_list):
            block = hex_list[i:i + block_size**2]
            if len(block) < block_size**2:
                block = self.apply_random_padding(block, block_size)
            blocks.append(block)
            i += block_size**2
        print(f"blocks: {blocks}\n")
        return blocks

    def conversion_into_matrices(self, hex_list):
        """Convert hex blocks into square matrices of uniform size."""
        matrix_size = self.choose_matrix_size(len(hex_list))  # Choose a fixed size
        blocks = self.split_blocks(hex_list, matrix_size)
        matrices = []

        for block in blocks:
            matrix = np.array([
                [int(block[i + j], 16) for j in range(matrix_size)]
                for i in range(0, len(block), matrix_size)
            ])
            matrices.append(matrix)
            print(f"matrix: {matrix}")
        return matrices

    def matrix_multiplication(self, matrices):
        """Perform chained matrix multiplication with proper dimensions."""
        if len(matrices) == 1:
            return matrices[0]

        def mat_mult(A, B):
            print(f"\nMultiplying Matrices:\n{A}\nAND\n{B}")
            return np.mod(np.matmul(A, B), 256)

        return reduce(mat_mult, matrices)

    def single_matrix_operations(self, matrices):
        self.matrices = []
        self.operation_sequences = []
        for matrix in matrices:
            modified_matrix, operations = apply_random_operations(matrix)
            self.matrices.append(modified_matrix)
            self.operation_sequences.append(operations)

    def round_matrix_operation(self):
        for _ in range(9):
            self.single_matrix_operations(self.matrices)
            result = self.matrix_multiplication(self.matrices)
            print(f"result: {result}")
            print("=================================================")


if __name__ == "__main__":
    enc = Encryption()
    plain_text = input("Enter the string: ")

    hex_string = enc.string_to_hex(plain_text)
    hex_list = [hex_string[i:i+2] for i in range(0, len(hex_string), 2)]
    matrices = enc.conversion_into_matrices(hex_list)
    enc.single_matrix_operations(matrices)
    for matrix in enc.matrices:
        print(matrix)

    result_matrix = enc.matrix_multiplication(enc.matrices)

    for i, matrix in enumerate(enc.matrices):
            print(f"\nMatrix {i+1} after operations:\n{matrix}")
            print(f"Matrix {i+1} applied operations: {', '.join(map(str, enc.operation_sequences[i]))}")
    print("\nResultant Matrix:\n", result_matrix)
