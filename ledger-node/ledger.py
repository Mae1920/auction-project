from flask import Flask, request, jsonify
import hashlib
import json
import time
import uuid

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

@app.route("/transaction", methods=["POST"])
def add_transaction():
    data = request.json

    if not data or "user" not in data or "amount" not in data:
        return {"error": "invalid transaction"}, 400

    transaction = {
        "id": str(uuid.uuid4()),
        "user": data["user"],
        "amount": data["amount"]
    }

    current_transactions.append(transaction)

    return {"status": "added to pending"}


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