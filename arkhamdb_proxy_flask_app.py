from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)

ARKHAMDB_BASE = "https://arkhamdb.com/api/public"

# --- Routes ---

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Arkham Proxy is live! Use /status, /cards, /cards/<pack_code>, /taboos, or /deck/<deck_id>."
    })

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "ArkhamDB proxy is running!"})

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

@app.route("/deck/<deck_id>", methods=["GET"])
def get_deck(deck_id):
    """
    Fetch a community deck from ArkhamDB and return it as plain text or JSON.
    Example:
      /deck/53986              → plain text export
      /deck/53986?format=json  → JSON export
    """
    export_format = request.args.get("format", "plain")  # "plain" or "json"
    url = f"https://arkhamdb.com/decklist/export/{export_format}/{deck_id}"

    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"error": f"Failed to fetch deck {deck_id}"}), response.status_code

    if export_format == "json":
        return jsonify(response.json())  # ArkhamDB already returns valid JSON
    return response.text

# --- Main entrypoint ---
if __name__ == "__main__":
    # ✅ Use dynamic port (for Render) or default to 5000 (local dev)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
