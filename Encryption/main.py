class Encryption:
    def __init__(self):
        self.hex_string = ""
        self.matrices = []

    def string_to_hex(self, string):
        self.hex_string = ''.join([hex(ord(char))[2:].zfill(2) for char in string])  # Ensure two-digit hex

    def conversion_into_matrices(self):
        hex_list = list(self.hex_string)  # Convert hex_string into a list of single characters

        while len(hex_list) % 16 != 0:
            hex_list.append('0')  # Padding if necessary

        self.matrices = [
            [hex_list[i + j:i + j + 4] for j in range(0, 16, 4)]
            for i in range(0, len(hex_list), 16)
        ]  # Convert into multiple 4x4 matrices

    def single_matrix_operations(self, matrices):
        print(f"matrices: {matrices}")
        # apply transpose of matrix
        matrices = [list(map(list, zip(*matrix))) for matrix in matrices]
        print(f"transpose matrices: {matrices}")

        # Shift Rows
        for matrix in matrices:
            print(f"Original Matrix: {matrix}")
            for i, row in enumerate(matrix):
                print(f"matrix[{i}]: {row}")
                if i == 1:
                    matrix[i] = [row[-1]] + row[:-1]
                elif i == 2:
                    row[0], row[2] = row[2], row[0]
                elif i == 3:
                    matrix[i] = row[1:] + [row[0]]
            print(f"Modified Matrix: {matrix}\n")

        # matrix Multiplication
        for matrix in matrices:
            pass

    def round_matrix_operation(self):
        for _ in range(9):
            self.single_matrix_operations(self.matrices)
            print("=================================================")


if __name__ == "__main__":
    encryption = Encryption()
    plain_text = input("Enter the string: ")

    encryption.string_to_hex(plain_text)
    encryption.conversion_into_matrices()
    encryption.round_matrix_operation()
    print(f"final matrices: {encryption.matrices}")
