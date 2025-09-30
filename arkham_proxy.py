import json

TABOO_CACHE_FILE = "taboos_cache.json"

@app.route("/taboos", methods=["GET"])
def get_taboos():
    url = f"{ARKHAMDB_BASE}/taboos.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Cache latest successful taboo list
        with open(TABOO_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)

        return jsonify(data)

    except requests.exceptions.RequestException as e:
        # If ArkhamDB fails, try cached taboo list
        if os.path.exists(TABOO_CACHE_FILE):
            with open(TABOO_CACHE_FILE, "r", encoding="utf-8") as f:
                cached = json.load(f)
            return jsonify({
                "warning": "ArkhamDB failed, serving cached taboo list",
                "data": cached
            }), 200
        return jsonify({"error": f"Failed to fetch taboo list: {e}"}), 502
