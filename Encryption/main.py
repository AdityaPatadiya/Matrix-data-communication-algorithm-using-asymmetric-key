import hashlib
import secrets
import json
import os

import sys
sys.path.append('/home/aditya/matrix_data_communication_algo/Matrix-data-communication-algorithm-using-asymmetric-key/')
from database import Database
from encryption import Encryption
from key_generation.SPHINCS_plus_signature import add_signature


class main:
    def __init__(self):
        self.random_values = {}
        self.message_id = ""
        self.data = {}
        self.enc = Encryption()
        self.db = Database()

    def generate_message_id(self, message: str) -> str:
        """Generate a unique ID for each message using SHA-256 and a random salt."""
        salt = secrets.token_hex(16)
        data = message + salt
        self.message_id = hashlib.sha256(data.encode()).hexdigest()

    def storing_operation_values(self):
        operation_values = {}
        for i in range(len(self.enc.matrices)):
            operation_values[i+1] = ', '.join(map(str, self.enc.operation_sequences[i]))
        return operation_values

    def storing_random_values(self):
        self.random_values["padding"] = self.enc.padding
        self.random_values["matrix_operations"] = self.storing_operation_values()

    def data_store(self):
        self.storing_random_values()
        self.data[self.message_id] = self.random_values
        # self.db.insert_data(self.message_id, self.random_values["padding"], self.random_values["matrix_operations"])
        # print("Data successfully stored in database.")
        if os.path.exists("Encrypted_data.json"):
            with open("Encrypted_data.json", 'r') as file:
                try:
                    existing_data = json.load(file)
                except json.JSONDecodeError:
                    existing_data = {}
        else:
            existing_data = {}
        existing_data[self.message_id] = self.random_values
        with open("Encrypted_data.json", 'w') as file:
            json.dump(existing_data, file, indent=4)

        print("✅ Data successfully stored in JSON file.")

    def main(self):
        plain_text = input("Enter the string: ")
        self.generate_message_id(plain_text)

        hex_string = self.enc.string_to_hex(plain_text)
        hex_list = [hex_string[i:i+2] for i in range(0, len(hex_string), 2)]
        matrices = self.enc.conversion_into_matrices(hex_list)
        self.enc.single_matrix_operations(matrices)

        print("\n======================== Final matrices after performing operations ========================")
        for matrix in self.enc.matrices:
            print(matrix)

        result_matrix = self.enc.matrix_multiplication(self.enc.matrices)

        print("\nResultant Matrix:\n", result_matrix)
        signed_matrix = add_signature(result_matrix)
        print(f"signed_matrix: {signed_matrix}")

        print("\n======================== Final data stored ========================")
        self.data_store()
        print(self.data)
        # self.db.close_connection()


if __name__ == "__main__":
    main_program = main()
    main_program.main()
