import numpy as np
from functools import reduce

from utils import apply_random_operations


class Encryption:
    def __init__(self):
        self.hex_string = ""
        self.matrices = []
        self.MATRIX_SIZES = [2, 3, 4, 6]
        # self.operation_sequences = []

    def string_to_hex(self, string):
        """Convert a string into hex representation."""
        hex_string = ''.join([hex(ord(char))[2:].zfill(2) for char in string])
        return hex_string

    def choose_matrix_size(self, data_length):
        """Choose the largest matrix size that can be consistently used."""
        for size in reversed(self.MATRIX_SIZES):
            if data_length >= size**2:
                return size
        return 2

    def apply_pkcs7_padding(self, hex_list, block_size):
        """Apply PKCS#7 padding so that the block is a perfect square matrix."""
        padding_needed = block_size**2 - len(hex_list)
        padding_value = hex(padding_needed)[2:].zfill(2)  # PKCS#7 padding
        hex_list.extend([padding_value] * padding_needed)
        return hex_list

    def split_blocks(self, hex_list, block_size):
        """Split hex data into consistent-sized matrices."""
        blocks = []
        i = 0
        while i < len(hex_list):
            block = hex_list[i:i + block_size**2]
            if len(block) < block_size**2:
                block = self.apply_pkcs7_padding(block, block_size)
            blocks.append(block)
            i += block_size**2
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
        # apply transpose of matrix
        # matrices = [list(map(list, zip(*matrix))) for matrix in matrices]
        # print(f"transpose matrices: {matrices}")

        # # Shift Rows
        # for matrix in matrices:
        #     for i, row in enumerate(matrix):
        #         if i == 1:
        #             matrix[i] = [row[-1]] + row[:-1]
        #         elif i == 2:
        #             row[0], row[2] = row[2], row[0]
        #         elif i == 3:
        #             matrix[i] = row[1:] + [row[0]]
        # self.matrices = matrices
        # print(f"matrices: {matrices}")
        print("method called.")
        self.matrices = [apply_random_operations(matrix) for matrix in matrices]

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
    # result_matrix = encryption.matrix_multiplication(matrices)
    # encryption.round_matrix_operation()
    enc.single_matrix_operations(matrices)
    for matrix in enc.matrices:
        print(matrix)
    # print("\nResultant Matrix:\n", result_matrix)
