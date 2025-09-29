from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

ARKHAMDB_BASE = "https://arkhamdb.com/api/public"

@app.route("/cards", methods=["GET"])
def get_all_cards():
    include_encounter = request.args.get("encounter", "0") == "1"
    url = f"{ARKHAMDB_BASE}/cards.json"
    if include_encounter:
        url += "?encounter=1"
    response = requests.get(url)
    return jsonify(response.json())

@app.route("/cards/<pack_code>", methods=["GET"])
def get_pack_cards(pack_code):
    url = f"{ARKHAMDB_BASE}/cards/{pack_code}.json"
    response = requests.get(url)
    return jsonify(response.json())

@app.route("/taboos", methods=["GET"])
def get_taboos():
    url = f"{ARKHAMDB_BASE}/taboos.json"
    response = requests.get(url)
    return jsonify(response.json())

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "ArkhamDB proxy is running!"})

# ✅ New root route
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Arkham Proxy is live! Use /status, /cards, /cards/<pack_code>, or /taboos."
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
