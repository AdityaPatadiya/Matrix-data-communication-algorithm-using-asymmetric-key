import json
import numpy as np
from sympy import mod_inverse
from Encryption.utils import circular_shift_column, circular_shift_row, transpose

# Mapping from code to function name
reverse_op_map = {
    1: "circular_shift_row",
    2: "circular_shift_column",
    3: "row_permutation",
    4: "column_permutation",
    5: "transpose",
    6: "modular_exponentiation",
    7: "lwe_noise"
}

# ---------- helpers for ASCII preference and discrete roots mod 256 ----------

PRINTABLE_ASCII = set(range(32, 127)) | {9, 10, 13}  # tab, LF, CR

def candidates_for_pow_mod_256(y, e, mod=256):
    """Return all x in 0..255 such that pow(x, e, 256) == y."""
    # Small table/cache speeds this up massively across many bytes
    # Build once per exponent
    return [x for x in range(256) if pow(x, e, mod) == y]

def choose_candidate(candidates):
    # If no candidates, return None
    if not candidates:
        return None

    # Filter to printable ASCII
    printable = [c for c in candidates if 32 <= c <= 126]

    if len(printable) == 1:
        return printable[0]

    if len(printable) > 1:
        # Prioritize letters first (a-z, A-Z)
        letters = [c for c in printable if (65 <= c <= 90) or (97 <= c <= 122)]
        if letters:
            return letters[0]  # pick first letter
        return printable[0]  # otherwise pick first printable

    # If no printable, just return the first candidate
    return candidates[0]

def invert_modexp_matrix_best_effort(Y, e, mod=256, verbose=False):
    Y = np.asarray(Y, dtype=int)
    H, W = Y.shape
    X = np.zeros_like(Y)
    ambiguous = 0
    no_solution = 0

    cand_cache = {}
    for i in range(H):
        for j in range(W):
            y = int(Y[i, j]) % mod
            if y not in cand_cache:
                cand_cache[y] = [x for x in range(256) if pow(x, e, mod) == y]
            cands = cand_cache[y]

            choice = choose_candidate(cands)
            if choice is None:
                no_solution += 1
                choice = 0
            else:
                if len(cands) > 1:
                    ambiguous += 1
                    if verbose:
                        print(f"[modexp inverse] y={y} has {len(cands)} candidates; picked {choice}; all={cands}")
            X[i, j] = choice

    stats = {"ambiguous_cells": ambiguous, "no_solution_cells": no_solution}
    return X, stats

def reverse_operations(matrix, operation_sequence, verbose=True):
    for op_code, data in reversed(operation_sequence):
        if op_code == 5:  # transpose
            if verbose: print("Reversing transpose")
            matrix = np.transpose(matrix)

        elif op_code == 3:  # row_permutation
            if verbose: print("Reversing row permutation")
            inverse_indices = np.argsort(data)
            matrix = matrix[inverse_indices]

        elif op_code == 4:  # column_permutation
            if verbose: print("Reversing column permutation")
            inverse_indices = np.argsort(data)
            matrix = matrix[:, inverse_indices]

        elif op_code == 1:  # circular_shift_row
            if verbose: print("Reversing row shift")
            # Encryption always used 'left'? Then reverse is 'right'
            matrix = np.array([np.roll(row, 1) for row in matrix])

        elif op_code == 2:  # circular_shift_column
            if verbose: print("Reversing column shift")
            matrix = np.array([np.roll(matrix[:, i], 1) for i in range(matrix.shape[1])]).T

        elif op_code == 6:  # modular_exponentiation
            # 'data' can be either an int exponent (legacy) or a dict with {'e': exponent, 'even_values': [...]}
            if isinstance(data, dict):
                exponent = int(data.get("e"))
                even_values = np.array(data.get("even_values"), dtype=int)
            else:
                exponent = int(data)
                even_values = None

            if verbose: print(f"Reversing modular exponentiation with exponent {exponent}")

            # First, best-effort inverse for all cells (gets unique results for odd residues)
            inv_guess, _stats = invert_modexp_matrix_best_effort(matrix, exponent, mod=256, verbose=False)

            # If we have recorded even preimages, apply them wherever the ciphertext cell is 0 and the record is not -1
            if even_values is not None:
                # positions where encryption output was 0 AND we recorded the original even value
                use_record = (matrix == 0) & (even_values >= 0)
                inv_guess = np.where(use_record, even_values, inv_guess)

            matrix = inv_guess

        elif op_code == 7:  # lwe_noise
            noise = np.array(data)
            if verbose: print("Reversing LWE noise")
            matrix = (matrix - noise) % 256

        else:
            raise ValueError(f"Unknown op_code: {op_code}")

    return matrix

def parse_operations(ops_string):
    """Parse operation string like '(3, [1, 2, 0]), (7, [[...noise...]])' into list of tuples."""
    ops = []
    parts = ops_string.split("), (")
    for p in parts:
        p = p.strip("()")
        code, param = p.split(",", 1)
        code = int(code.strip())
        param = eval(param.strip())  # Convert to Python object
        ops.append((code, param))
    return ops

def split_combined_matrix(combined_matrix):
    """Split a combined matrix with comma-separated values into separate numpy matrices."""
    # Count how many matrices are combined based on first element
    num_matrices = len(combined_matrix[0][0].split(","))
    
    # Initialize separate matrices
    matrices = [np.zeros((len(combined_matrix), len(combined_matrix[0])), dtype=int) for _ in range(num_matrices)]
    
    # Fill matrices
    for i in range(len(combined_matrix)):
        for j in range(len(combined_matrix[0])):
            values = combined_matrix[i][j].split(",")
            for k, val in enumerate(values):
                matrices[k][i, j] = int(val)
    
    return matrices


def decrypt_combined_matrix(message_id, combined_matrix, metadata_file):
    """Decrypt combined matrix that contains multiple matrices joined by commas."""
    # Step 1: Split combined matrix
    matrices = split_combined_matrix(combined_matrix)

    # Step 2: Load metadata
    with open(metadata_file, "r") as f:
        metadata = json.load(f)

    if message_id not in metadata:
        raise ValueError("Message ID not found")

    msg_data = metadata[message_id]
    padding = msg_data["padding"]
    matrix_ops = msg_data["matrix_operations"]

    # Step 3: Reverse operations for each matrix
    for idx, matrix in enumerate(matrices, start=1):
        key = str(idx)
        if key in matrix_ops:
            ops_string = matrix_ops[key]
            ops = parse_operations(ops_string)
            matrices[idx - 1] = reverse_operations(matrix, ops)

    # Step 4: Flatten all matrices into one list
    all_values = []
    for m in matrices:
        all_values.extend(m.flatten(order='C').tolist())

    # Step 5: Remove padding
    if isinstance(padding, int):
        all_values = all_values[:-padding] if padding > 0 else all_values
    elif isinstance(padding, str):
        all_values = all_values[:-len(padding)]
    elif isinstance(padding, list):
        all_values = all_values[:-len(padding)]

    # Debug before hex conversion
    print("Final reversed values:", all_values[:50], "... total:", len(all_values))

    # Step 6: Convert to hex and then to original text
    decoded_chars = []
    for v in all_values:
        if 32 <= v <= 126 or v in (9, 10, 13):  # Printable ASCII or whitespace
            decoded_chars.append(chr(v))
        else:
            decoded_chars.append('?')  # placeholder for unprintable
    original_text = "".join(decoded_chars)

    return original_text


# combined_matrix =  [
#     ['76,249', '107,0', '110,55'],
#     ['95,0', '33,81', '76,0'],
#     ['107,119', '116,99', '112,147']
#  ]

# message_id = "01b6a3cd9694132a0564b811ec2a4e03ea5836e3de6aaa611ee895818160a9b3"
# original_text = decrypt_combined_matrix(message_id, combined_matrix, "Data_utils.json")
# print("Decrypted text:", original_text)
