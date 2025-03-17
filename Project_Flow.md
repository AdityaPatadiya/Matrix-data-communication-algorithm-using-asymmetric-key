Step-1: Enter the string.
step-2: convert into the hex
step-3: convert the hex string into the 2 character blocks with `split_blocks` method after padding rest elements with `PKCS#7` padding method.
step-4: the hex_list will convert into the matrices(list of matrix) with appropeiate size based on the length of hex_list and store into the matrices variable which is `matrices`.
step-5: apply the operation on the matrices and it will store in the matrices instance which is `self.matrices`.
step-6: after operation, it will multiply with each other and generate the single matrix.