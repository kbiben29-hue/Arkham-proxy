from flask import Flask, jsonify, request
import requests
import os
import time

app = Flask(__name__)

ARKHAMDB_BASE = "https://arkhamdb.com/api/public"

# --- Cache for taboos ---
TABOO_CACHE = None
TABOO_CACHE_TIME = 0
TABOO_CACHE_TTL = 3600  # 1 hour


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
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": f"Failed to fetch cards: {e}"}), 500


@app.route("/cards/<pack_code>", methods=["GET"])
def get_pack_cards(pack_code):
    url = f"{ARKHAMDB_BASE}/cards/{pack_code}.json"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": f"Failed to fetch pack {pack_code}: {e}"}), 500


@app.route("/taboos", methods=["GET"])
def get_taboos():
    global TABOO_CACHE, TABOO_CACHE_TIME

    # Serve from cache if recent
    if TABOO_CACHE and (time.time() - TABOO_CACHE_TIME < TABOO_CACHE_TTL):
        return jsonify(TABOO_CACHE)

    url = f"{ARKHAMDB_BASE}/taboos.json"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        TABOO_CACHE = response.json()
        TABOO_CACHE_TIME = time.time()
        return jsonify(TABOO_CACHE)
    except Exception as e:
        if TABOO_CACHE:
            # Serve stale cache if available
            return jsonify(TABOO_CACHE)
        return jsonify({"error": f"Failed to fetch taboos: {e}"}), 500


@app.route("/deck/<deck_id>", methods=["GET"])
def get_deck(deck_id):
    """
    Fetch a community deck from ArkhamDB and return it as plain text or JSON.
    Example:
      /deck/57391              → plain text export
      /deck/57391?format=json  → JSON export
    """
    export_format = request.args.get("format", "plain")  # "plain" or "json"
    url = f"https://arkhamdb.com/deck/export/{export_format}/{deck_id}"

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        if export_format == "json":
            return jsonify(response.json())
        return response.text
    except Exception as e:
        return jsonify({"error": f"Failed to fetch deck {deck_id}: {e}"}), 500


# --- Main entrypoint ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
