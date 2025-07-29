import numpy as np
from Encryption.utils import (circular_shift_row, circular_shift_column, row_permutation, column_permutation, transpose, modular_exponentiation, lwe_noise)


class matrix_decryption:
    def split_matrix(self, merged_matrix):
        """Split a merged matrix of form 'X,Y' into two separate matrices."""
        row_count, col_count = merged_matrix.shape
        matrixA = np.zeros((row_count, col_count), dtype=int)
        matrixB = np.zeros((row_count, col_count), dtype=int)

        for i in range(row_count):
            for j in range(col_count):
                a, b = merged_matrix[i,j].split(',')
                matrixA[i,j] = int(a)
                matrixB[i,j] = int(b)
        print("Matrix A:\n", matrixA)
        print("Matrix B:\n", matrixB)

        return matrixA, matrixB
    
    def reverse_operations(self,matrix, operations):
        """Reverse a sequence of operations on the encrypted matrix."""
        for op_code, param in reversed(operations):
            if op_code == 1:  # circular shift row
                direction = 'right'  # reverse left by shifting right
                matrix = circular_shift_row(matrix, direction)

            elif op_code == 2:  # circular shift column
                direction = 'down'  # reverse up by shifting down
                matrix = circular_shift_column(matrix, direction)

            elif op_code == 3:  # row_permutation
                indices = param
                reverse_indices = [0] * len(indices)
                for i, j in enumerate(indices):
                    reverse_indices[j] = i
                matrix = matrix[reverse_indices]

            elif op_code == 4:  # column_permutation
                indices = param
                reverse_indices = [0] * len(indices)
                for i, j in enumerate(indices):
                    reverse_indices[j] = i
                matrix = matrix[:, reverse_indices]

            elif op_code == 5:  # transpose
                matrix = transpose(matrix)

            elif op_code == 6:  # modular exponentiation
                exponent = param
                # To reverse, we need the modular inverse of the exponent
                mod = 256
                inv = pow(exponent, -1, mod-1)  # Fermat/Euler inverse
                matrix = np.mod(np.power(matrix, inv), mod)

            elif op_code == 7:  # lwe_noise
                noise = np.array(param)
                matrix = np.mod(matrix - noise, 256)

        return matrix


matrix_dec = matrix_decryption()
matrix_dec.split_matrix(np.array([['107,0', '72,33', '106,225'], ['37,0', '101,0', '74,0'], ['114,193', '116,0', '110,241']]))
