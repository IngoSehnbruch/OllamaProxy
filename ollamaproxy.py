from flask import Flask, request, jsonify
import requests

import os
from dotenv import load_dotenv

load_dotenv()

LISTEN_PORT = os.getenv("LISTEN_PORT", None)
FORWARD_PORT = os.getenv("FORWARD_PORT", None)
AUTH_TOKEN = os.getenv("AUTH_TOKEN", None)
MASTER_TOKEN = os.getenv("MASTER_TOKEN", None)
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
DEBUG = True
if LISTEN_PORT is None or FORWARD_PORT is None or AUTH_TOKEN is None:
    print("Error: Missing environment variables in .env file")
    exit(1)

app = Flask(__name__)

#* Basic auth check for incoming requests
def check_auth(request, require_master=False):
    try:
        token = request.headers.get("Authorization")
        if token is None:
            if DEBUG: print("No Authorization header found")
            return False
        token = token.split("Bearer ")[1]
        if DEBUG: print("Token:", token, AUTH_TOKEN)
    except:
        if DEBUG: print("Unknown Authorization Error")
        return False
    
    if require_master:
        if MASTER_TOKEN is None:
            if DEBUG: print("Warning: Master token not set")
            return False
        return (token == MASTER_TOKEN)
    else:
        return (token == AUTH_TOKEN) # or token == MASTER_TOKEN
    


@app.route("/api/generate", methods=["POST"])
def proxy_generate():    
    if check_auth(request) is False:
        if DEBUG: print("Unauthorized request:", request)
        return jsonify({"error": "Unauthorized"}), 401
    
    response = requests.post("http://localhost:" + FORWARD_PORT + "/api/generate", json=request.json)
    if DEBUG: print("GENERATED-RESPONSE:", response)
    return (response)


@app.route("/api/chat", methods=["POST"])
def proxy_chat():    
    if check_auth(request) is False:
        if DEBUG: print("Unauthorized request:", request)
        return jsonify({"error": "Unauthorized"}), 401
    
    response = requests.post("http://localhost:" + FORWARD_PORT + "/api/chat", json=request.json)
    if DEBUG: print("CHAT-RESPONSE:", response)
    return (response.content, response.status_code, response.headers.items())

if __name__ == "__main__":
    print("Running OllamaProxy on port", LISTEN_PORT)
    app.run(port=LISTEN_PORT)
