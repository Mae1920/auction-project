from flask import Flask, request, jsonify
import hashlib
import json
import time
import uuid
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

app = Flask(__name__)

blockchain = []
current_transactions = []

def create_block(previous_hash, nonce):
    block = {
        "index": len(blockchain) + 1,
        "timestamp": time.time(),
        "transactions": current_transactions.copy(),
        "previous_hash": previous_hash,
        "nonce": nonce
    }

    blockchain.append(block)
    current_transactions.clear()

    return block

def hash_block(block):
    block_string = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

def proof_of_work(previous_hash):
    nonce = 0

    while True:
        block = {
            "index": len(blockchain) + 1,
            "timestamp": time.time(),
            "transactions": current_transactions,
            "previous_hash": previous_hash,
            "nonce": nonce
        }

        hash_result = hash_block(block)

        if hash_result.startswith("000"):
            return nonce

        nonce += 1

def verify_signature(transaction):
    try:
        public_key = serialization.load_pem_public_key(
            transaction["public_key"].encode()
        )

        signature = bytes.fromhex(transaction["signature"])

        message = json.dumps({
            "user": transaction["user"],
            "amount": transaction["amount"]
        }, sort_keys=True).encode()

        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return True
    except Exception:
        return False


@app.route("/transaction", methods=["POST"])
def add_transaction():
    data = request.json

    required = ["user", "amount", "signature", "public_key"]

    if not all(k in data for k in required):
        return {"error": "invalid transaction format"}, 400

    if not verify_signature(data):
        return {"error": "invalid signature"}, 400

    transaction = {
        "id": str(uuid.uuid4()),
        "user": data["user"],
        "amount": data["amount"]
    }

    current_transactions.append(transaction)

    return {"status": "verified and added"}


@app.route("/mine", methods=["GET"])
def mine():
    if len(current_transactions) == 0:
        return {"error": "no transactions to mine"}, 400

    if len(blockchain) == 0:
        previous_hash = "0"
    else:
        previous_hash = hash_block(blockchain[-1])

    nonce = proof_of_work(previous_hash)

    block = create_block(previous_hash, nonce)

    return block


@app.route("/chain", methods=["GET"])
def get_chain():
    return jsonify(blockchain)

# Create genesis block
if len(blockchain) == 0:
    create_block("0", 0)  

app.run(host="0.0.0.0", port=5001)