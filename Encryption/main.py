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
    

if __name__ == "__main__":
    encryption = Encryption()
    plain_text = input("Enter the string: ")

    encryption.string_to_hex(plain_text)
    encryption.conversion_into_matrices()
    print(encryption.matrices)
