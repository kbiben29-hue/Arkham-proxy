from flask import Flask, Response
import requests

app = Flask(__name__)

# Replace this with your real cookie from Safari DevTools
COOKIE = {"PHPSESSID": "your_cookie_here"}

@app.route("/")
def home():
    return {"status": "ArkhamDB proxy is running!"}

@app.route("/cards")
def cards():
    url = "https://arkhamdb.com/api/public/cards/"
    r = requests.get(url, cookies=COOKIE)
    return Response(r.content, status=r.status_code, content_type=r.headers["content-type"])

@app.route("/taboos")
def taboos():
    url = "https://arkhamdb.com/api/public/taboos/"
    r = requests.get(url, cookies=COOKIE)
    return Response(r.content, status=r.status_code, content_type=r.headers["content-type"])

@app.route("/deck/<deck_id>")
def deck(deck_id):
    url = f"https://arkhamdb.com/decklist/view/{deck_id}"
    r = requests.get(url, cookies=COOKIE)
    return Response(r.content, status=r.status_code, content_type=r.headers["content-type"])
