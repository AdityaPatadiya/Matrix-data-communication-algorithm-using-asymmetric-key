# Matrix-data-communication-algorithm-using-asymmetric-key

A PQC(Post-Quantum Cryptography) algorithm that provides secyrity from security threads like quantum attacks for data communication that will enhance the security and provides a robust way to exchange the information.

- It uses **Kyber** algorithm for Key exchange and **SPHINCS+** algorithm for signature.

- It is a hybrid approach of **aes_gcm-kyber** for securing the future.

## How it works?
1. Take the data from the user.
2. convert it into hex.
3. then it convert into matrix and for that it will add padding if needed.
4. Random operations will apply to the matrix for providing string obfucation to the message.
5. kyber will generate the secret key that will used as **aes_key** and encrypt the matrix.
6. kyber will encapsulate the **aes_key**.
7. **SPHINCS+** will provide signature to ensure the integrity of the message.


- Use Linux system to setup this project.

## How to setup for your device?
1. fork this repo
2. clone you repo with the command: `git clone https://github.com/<Your_User_Name>/Matrix-data-communication-algorithm-using-asymmetric-key/` 
3. create a venv: `python3 -m venv venv`
4. install required packages: `pip install -r requirements.txt`
5. ```
    sudo apt update
    sudo apt install cmake gcc ninja-build python3-pip libssl-dev libtool autoconf automake
    ```
6. ```
    git clone --recursive https://github.com/open-quantum-safe/liboqs.git
    cd liboqs
    ```
7. ```
    mkdir build && cd build
    cmake -GNinja -DBUILD_SHARED_LIBS=ON ..
    ninja
    ```
    You will now have `liboqs.so` inside `liboqs/build/lib/`.
8. run the command: `export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/lib`
9. ```
    echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/path/to/liboqs/build/lib' >> ~/.bashrc
    source ~/.bashrc
    ```
