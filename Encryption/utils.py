import numpy as np
import random

# operation_map = {
#     "circular_shift_row": 1,
#     "circular_shift_column": 2,
#     "row_permutation": 3,
#     "column_permutation": 4,
#     "transpose": 5,
#     "modular_exponentiation": 6,
#     "lwe_noise": 7
# }

def modular_exponentiation(matrix, exponent=3, mod=256):
    """Apply modular exponentiation to each element in the matrix."""
    return np.mod(np.power(matrix, exponent), mod)

def lwe_noise(matrix, noise_scale=5):
    """Apply Learning With Errors (LWE) noise to the matrix."""
    noise = np.random.randint(-noise_scale, noise_scale + 1, matrix.shape)
    return np.mod(matrix + noise, 256)

def circular_shift_row(matrix, direction='left'):
    """Perform circular shift on rows either left or right."""
    return np.array([np.roll(row, -1 if direction == 'left' else 1) for row in matrix])

def circular_shift_column(matrix, direction='up'):
    """Perform circular shift on columns either up or down."""
    if matrix.shape[1] == 0:  # Ensure matrix has columns
        return matrix
    return np.array([np.roll(matrix[:, i], -1 if direction == 'up' else 1) for i in range(matrix.shape[1])]).T

def row_permutation(matrix):
    """Randomly shuffle the rows of the matrix."""
    return matrix[np.random.permutation(matrix.shape[0])]

def column_permutation(matrix):
    """Randomly shuffle the columns of the matrix."""
    return matrix[:, np.random.permutation(matrix.shape[1])]

def transpose(matrix):
    """Transpose the matrix."""
    return np.transpose(matrix)

def apply_random_operations(matrix):
    """Apply a random sequence of operations (linear → non-linear → linear → non-linear)."""
    linear_operations = [circular_shift_row, circular_shift_column, row_permutation, column_permutation, transpose]
    non_linear_operations = [modular_exponentiation, lwe_noise]

    selected_operations = [
        random.choice(linear_operations),
        random.choice(non_linear_operations),
        random.choice(linear_operations),
        random.choice(non_linear_operations)
    ]

    # operation_sequence = []
    # for operation in selected_operations:
    #     matrix = operation(matrix)
    #     operation_sequence.append(operation_map[operation.__name__])

    for operation in selected_operations:
        matrix = operation(matrix)

    return matrix
