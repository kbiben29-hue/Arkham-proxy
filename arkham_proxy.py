from flask import Flask, jsonify, request
import requests
import os
import json

app = Flask(__name__)

ARKHAMDB_BASE = "https://arkhamdb.com/api/public"
TABOO_CACHE_FILE = "taboos_cache.json"

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
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch cards: {e}"}), 502

@app.route("/cards/<pack_code>", methods=["GET"])
def get_pack_cards(pack_code):
    url = f"{ARKHAMDB_BASE}/cards/{pack_code}.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch cards for pack {pack_code}: {e}"}), 502

@app.route("/taboos", methods=["GET"])
def get_taboos():
    url = f"{ARKHAMDB_BASE}/taboos.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Cache the latest taboo list
        with open(TABOO_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)

        return jsonify(data)

    except requests.exceptions.RequestException as e:
        # If ArkhamDB fails, return cached taboo list if available
        if os.path.exists(TABOO_CACHE_FILE):
            with open(TABOO_CACHE_FILE, "r", encoding="utf-8") as f:
                cached = json.load(f)
            return jsonify({
                "warning": "ArkhamDB failed, serving cached taboo list",
                "data": cached
            }), 200
        return jsonify({"error": f"Failed to fetch taboo list: {e}"}), 502

@app.route("/deck/<deck_id>", methods=["GET"])
def get_deck(deck_id):
    """
    Fetch a community deck from ArkhamDB and return it as plain text or JSON.
    Example:
      /deck/57391              → plain text export
      /deck/57391?format=json  → JSON export
    """
    export_format = request.args.get("format", "plain")  # "plain" or "json"
    if export_format not in ["plain", "json"]:
        return jsonify({"error": "Invalid format. Use 'plain' or 'json'."}), 400

    url = f"https://arkhamdb.com/deck/export/{export_format}/{deck_id}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request to ArkhamDB timed out"}), 504
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"ArkhamDB returned an error: {e}"}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request failed: {e}"}), 502

    if export_format == "json":
        try:
            return response.json()
        except ValueError:
            return jsonify({"error": "Invalid JSON returned by ArkhamDB"}), 502

    return response.text, 200, {"Content-Type": "text/plain; charset=utf-8"}

# --- Main entrypoint ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
rned by ArkhamDB"}), 502

    return response.text, 200, {"Content-Type": "text/plain; charset=utf-8"}
