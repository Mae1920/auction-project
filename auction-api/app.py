from flask import Flask, request
import requests
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

app = Flask(__name__)

LEDGER_URL = "http://ledger-node:5001"

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

public_key = private_key.public_key()

def sign_transaction(data):
    message = json.dumps(data, sort_keys=True).encode()

    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    return signature.hex()

def get_public_key():
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()


@app.route("/bid", methods=["POST"])
def bid():
    data = request.json

    # 🔐 validar input
    if not data or "user" not in data or "amount" not in data:
        return {"error": "invalid input"}, 400

    try:
        tx = {
            "user": data["user"],
            "amount": data["amount"]
        }

        signature = sign_transaction(tx)

        tx["signature"] = signature
        tx["public_key"] = get_public_key()

        # 📡 enviar para ledger
        response = requests.post(f"{LEDGER_URL}/transaction", json=tx)

        # 🔎 verificar resposta do ledger
        if response.status_code != 200:
            return {
                "error": "ledger rejected transaction",
                "details": response.json()
            }, 400

        return {"status": "signed bid sent"}

    except Exception as e:
        return {"error": str(e)}, 500

app.run(host="0.0.0.0", port=5000)