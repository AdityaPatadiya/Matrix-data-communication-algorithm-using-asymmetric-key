import numpy as np
import secrets

from Encryption.utils import apply_random_operations


class stringObfucate:
    def __init__(self):
        self.hex_string = ""
        self.matrices = []
        self.padding = []
        self.MATRIX_SIZES = [2, 3, 4, 6]
        self.operation_sequences = []

    def string_to_hex(self, string):
        """Convert a string into hex representation."""
        hex_string = ''.join([hex(ord(char))[2:].zfill(2) for char in string])
        print(f"\nhex string: {hex_string}\n")
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
            self.padding = [secrets.token_hex(1) for _ in range(padding_needed)]
            hex_list.extend(self.padding)

        print(f"Random padding applied: {self.padding}\n")
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

        print("======================== Matrices before applying the operations. ========================")
        for block in blocks:
            matrix = np.array([
                [int(block[i + j], 16) for j in range(matrix_size)]
                for i in range(0, len(block), matrix_size)
            ])
            matrices.append(matrix)
            print(f"matrix: {matrix}\n")
        print("======================== operations used for matrices. ========================")
        return matrices

    def merge_matrices(self, matrices):
        """Merge multiple matrices by concatenating corresponding elements with ','."""
        merged_matrix = np.full(matrices[0].shape, "", dtype=object)

        for matrix in matrices:
            for i in range(matrix.shape[0]):
                for j in range(matrix.shape[1]):
                    if merged_matrix[i, j] == "":
                        merged_matrix[i, j] = str(matrix[i, j])
                    else:
                        merged_matrix[i, j] += "," + str(matrix[i, j])

        return merged_matrix

    def single_matrix_operations(self, matrices):
        self.matrices = []
        self.operation_sequences = []
        for matrix in matrices:
            modified_matrix, operations = apply_random_operations(matrix)
            self.matrices.append(modified_matrix)
            self.operation_sequences.append(operations)
