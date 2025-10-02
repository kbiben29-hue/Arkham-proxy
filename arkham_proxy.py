from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# pull ArkhamDB session cookie from environment variables
ARKHAM_COOKIE = os.getenv("ARKHAM_COOKIE")

@app.route("/")
def home():
    return {"status": "Arkham Proxy is running"}

@app.route("/fetch")
def fetch():
    url = request.args.get("url")
    if not url:
        return {"error": "No URL provided"}, 400

    headers = {}
    if ARKHAM_COOKIE:
        headers["Cookie"] = f"PHPSESSID={ARKHAM_COOKIE}"

    resp = requests.get(url, headers=headers)
    return resp.text, resp.status_code, {"Content-Type": resp.headers.get("Content-Type", "text/plain")}
