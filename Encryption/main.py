import numpy as np
from functools import reduce


class Encryption:
    def __init__(self):
        self.hex_string = ""
        self.matrices = []

    def string_to_hex(self, string):
        self.hex_string = ''.join([hex(ord(char))[2:].zfill(2) for char in string])  # Ensure two-digit hex
        print(self.hex_string)

    def conversion_into_matrices(self, string):
        hex_list = list(string)  # Convert hex_string into a list of single characters

        while len(hex_list) % 16 != 0:
            hex_list.append('0')  # Padding if necessary
        print(f"hex_list: {hex_list}")

        self.matrices = [
            [
                [int(hex_list[i + j + k], 16) for k in range(4)]  # Convert each hex char to int
                for j in range(0, 16, 4)
            ]
            for i in range(0, len(hex_list), 16)
        ]
        print(f"matrices after converting into matrix: {self.matrices}\n")

    def matrix_multiplication(self, matrices):
        def mat_mult(A, B):
            print(f"A: {A}")
            print(f"B: {B}")
            return (np.matmul(A, B)) % 256
        return reduce(mat_mult, matrices)

    def single_matrix_operations(self, matrices):
        # print(f"matrices: {matrices}")
        # apply transpose of matrix
        matrices = [list(map(list, zip(*matrix))) for matrix in matrices]
        print(f"transpose matrices: {matrices}")

        # Shift Rows
        for matrix in matrices:
            # print(f"Original Matrix: {matrix}")
            for i, row in enumerate(matrix):
                # print(f"matrix[{i}]: {row}")
                if i == 1:
                    matrix[i] = [row[-1]] + row[:-1]
                elif i == 2:
                    row[0], row[2] = row[2], row[0]
                elif i == 3:
                    matrix[i] = row[1:] + [row[0]]
            # print(f"Modified Matrix: {matrix}\n")
        self.matrices = matrices
        print(f"matrices: {matrices}")

        # matrix Multiplication
        result = self.matrix_multiplication(matrices)
        print(f"result: {result}")


    def round_matrix_operation(self):
        for _ in range(9):
            self.single_matrix_operations(self.matrices)
            print("=================================================")


if __name__ == "__main__":
    encryption = Encryption()
    plain_text = input("Enter the string: ")

    encryption.string_to_hex(plain_text)
    encryption.conversion_into_matrices(encryption.hex_string)
    print(f"initial matrices: {encryption.matrices}")
    encryption.round_matrix_operation()
    print(f"final matrices: {encryption.matrices}")
