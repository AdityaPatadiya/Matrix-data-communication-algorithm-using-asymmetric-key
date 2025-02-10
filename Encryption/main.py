from utils import string_to_hex, conversion_into_matrices, matrix_multiplication


class Encryption:
    def __init__(self):
        self.hex_string = ""
        self.matrices = []

    def single_matrix_operations(self, matrices):
        # apply transpose of matrix
        matrices = [list(map(list, zip(*matrix))) for matrix in matrices]
        print(f"transpose matrices: {matrices}")

        # Shift Rows
        for matrix in matrices:
            for i, row in enumerate(matrix):
                if i == 1:
                    matrix[i] = [row[-1]] + row[:-1]
                elif i == 2:
                    row[0], row[2] = row[2], row[0]
                elif i == 3:
                    matrix[i] = row[1:] + [row[0]]
        self.matrices = matrices
        print(f"matrices: {matrices}")

        # matrix Multiplication
        result = matrix_multiplication(matrices)
        print(f"result: {result}")


    def round_matrix_operation(self):
        for _ in range(9):
            self.single_matrix_operations(self.matrices)
            print("=================================================")


if __name__ == "__main__":
    encryption = Encryption()
    plain_text = input("Enter the string: ")

    encryption.hex_string = string_to_hex(plain_text)
    encryption.matrices = conversion_into_matrices(encryption.hex_string)
    encryption.round_matrix_operation()
    print(f"final matrices: {encryption.matrices}")
