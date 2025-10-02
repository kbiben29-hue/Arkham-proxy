from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

ARKHAMDB_BASE = "https://arkhamdb.com"

# --- Routes ---

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Arkham Proxy is live! Use /status or /deck/<deck_id>?format=json"
    })

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "ArkhamDB proxy is running!"})

@app.route("/deck/<deck_id>", methods=["GET"])
def get_deck(deck_id):
    """
    Fetch a community deck from ArkhamDB and return as JSON or plain text.
    Example:
      /deck/57391              → plain text export
      /deck/57391?format=json  → JSON export
    """
    export_format = request.args.get("format", "plain")  # plain or json
    if export_format not in ["plain", "json"]:
        return jsonify({"error": "Invalid format. Use 'plain' or 'json'."}), 400

    url = f"{ARKHAMDB_BASE}/deck/export/{export_format}/{deck_id}"

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

    # otherwise return plain text
    return response.text, 200, {"Content-Type": "text/plain; charset=utf-8"}


# --- Entry point (only used locally) ---
if __name__ == "__main__":
    app.run(debug=True)
