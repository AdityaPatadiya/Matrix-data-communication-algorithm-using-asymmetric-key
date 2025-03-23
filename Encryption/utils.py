import numpy as np
import secrets
from sympy import gcd

operation_map = {
    "circular_shift_row": 1,
    "circular_shift_column": 2,
    "row_permutation": 3,
    "column_permutation": 4,
    "transpose": 5,
    "modular_exponentiation": 6,
    "lwe_noise": 7
}


def modular_exponentiation(matrix, mod=256):
    """Apply modular exponentiation to each element in the matrix."""
    def get_random_exponent(mod=256):
        """Generate a secure random exponent ensuring it's invertible."""
        while True:
            e = secrets.randbelow(mod - 1) + 1  # Random number between 1 and 255
            if gcd(e, mod - 1) == 1:  # Ensure modular inverse exists
                return e
    exponent = get_random_exponent(mod)
    return np.mod(np.power(matrix, exponent), mod), exponent


def lwe_noise(matrix, noise_scale=5):
    """Apply Learning With Errors (LWE) noise to the matrix."""
    noise = np.array([[secrets.randbelow(2 * noise_scale + 1) - noise_scale for _ in range(matrix.shape[1])]
                      for _ in range(matrix.shape[0])])
    print(f"noise: {noise.tolist()}")
    return np.mod(matrix + noise, 256), noise.tolist()


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
    indices = list(range(matrix.shape[0]))
    secrets.SystemRandom().shuffle(indices)
    print(f"indices: {indices}")
    return matrix[indices], indices


def column_permutation(matrix):
    """Randomly shuffle the columns of the matrix."""
    indices = list(range(matrix.shape[1]))
    secrets.SystemRandom().shuffle(indices)
    print(f"indices: {indices}")
    return matrix[:, indices], indices


def transpose(matrix):
    """Transpose the matrix."""
    return np.transpose(matrix)


def apply_random_operations(matrix):
    """Apply a random sequence of operations (linear → non-linear → linear → non-linear)."""
    linear_operations = [circular_shift_row, circular_shift_column, row_permutation, column_permutation, transpose]
    non_linear_operations = [modular_exponentiation, lwe_noise]

    selected_operations = [
        secrets.choice(linear_operations),
        secrets.choice(non_linear_operations)
    ]

    operation_sequence = []
    for operation in selected_operations:
        op_code = operation_map[operation.__name__]

        if operation == row_permutation:
            matrix, row_indices = operation(matrix)
            operation_sequence.append((op_code, row_indices))

        elif operation == column_permutation:
            matrix, col_indices = operation(matrix)
            operation_sequence.append((op_code, col_indices))

        elif operation == lwe_noise:
            matrix, noise = operation(matrix)
            operation_sequence.append((op_code, noise))
        
        elif operation == modular_exponentiation:
            matrix, exponent = operation(matrix)
            operation_sequence.append((op_code, exponent))

        else:
            matrix = operation(matrix)
            operation_sequence.append((op_code, None))

    print(f"operations sequesces: {operation_sequence}")

    return matrix, operation_sequence
