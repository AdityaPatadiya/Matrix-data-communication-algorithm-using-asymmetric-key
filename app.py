# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from Encryption.main import encryptionMain

encryption = encryptionMain()

app = Flask(__name__)
CORS(app)  # Allow requests from your React frontend

@app.route("/")
def home():
    return "PQC Encryption API is running"

@app.route("/api/encrypt", methods=["POST"])
def encrypt():
    data = request.json
    plaintext = data.get("plaintext")

    if not plaintext:
        return jsonify({"error": "Missing 'plaintext' field"}), 400

    encrypted = encryption.main(plaintext)
    return jsonify({"ciphertext": encrypted})

# @app.route("/api/decrypt", methods=["POST"])
# def decrypt():
#     data = request.json
#     ciphertext = data.get("ciphertext")

#     if not ciphertext:
#         return jsonify({"error": "Missing 'ciphertext' field"}), 400

#     decrypted = pqc_decrypt(ciphertext)
#     return jsonify({"plaintext": decrypted})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
