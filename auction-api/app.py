from flask import Flask, request
import requests

app = Flask(__name__)

LEDGER_URL = "http://ledger-node:5001"

@app.route("/bid", methods=["POST"])
def bid():
    data = request.json

    requests.post(f"{LEDGER_URL}/transaction", json=data)

    return {"status": "bid sent"}

app.run(host="0.0.0.0", port=5000)