# Based on: https://github.com/ollama/ollama/blob/main/docs/api.md
# OllamaProxy is a simple proxy server that forwards requests to an Ollama server.
# Basic functionality includes two tokens for two levels of access control, 
# and the ability to control specific endpoints based on the token used.

from flask import Flask, request, jsonify
import requests

import os
from dotenv import load_dotenv
load_dotenv()

#* Config from environment variables (or .env file)
DEBUG = os.getenv("DEBUG", "false").lower() == "true"   # Debug mode for detailed logging

OLLAMA_HOST =       os.getenv("OLLAMA_HOST", "localhost") # Hostname of the Ollama server / container
LISTEN_PORT =       os.getenv("LISTEN_PORT", "80")  # Port to listen for incoming requests
FORWARD_PORT =      os.getenv("FORWARD_PORT", "11434") # Port of the Ollama server

PROTOCOL =          os.getenv("PROTOCOL", "http") # Protocol to use for forwarding requests (http or https)

#! Only alphanumeric characters and -._!?@ are allowed in the tokens:
AUTH_TOKEN =        os.getenv("AUTH_TOKEN", None)   # Required token for incoming requests
MASTER_TOKEN =      os.getenv("MASTER_TOKEN", None) # master token / None => disables routes that require master token
if MASTER_TOKEN == "": MASTER_TOKEN = None

# Check for missing required environment variables and exit if any are missing (master token is optional)
if LISTEN_PORT is None or FORWARD_PORT is None or AUTH_TOKEN is None:
    print("Error: Missing environment variables in .env file")
    exit(1)

#* Control which endpoints require the master token
ENDPOINTS = {
    #* defaults to false:
    "generate":     os.getenv("GENERATE_REQUIRES_MASTER", "false").lower() == "true",
    "chat":         os.getenv("CHAT_REQUIRES_MASTER", "false").lower() == "true",
    "list":         os.getenv("LIST_REQUIRES_MASTER", "false").lower() == "true",
    "show":         os.getenv("SHOW_REQUIRES_MASTER", "false").lower() == "true",
    #* defaults to true:
    "create":       os.getenv("CREATE_REQUIRES_MASTER", "true").lower() == "true",
    "copy":         os.getenv("COPY_REQUIRES_MASTER", "true").lower() == "true",
    "delete":       os.getenv("DELETE_REQUIRES_MASTER", "true").lower() == "true",
    "pull":         os.getenv("PULL_REQUIRES_MASTER", "true").lower() == "true",
    "push":         os.getenv("PUSH_REQUIRES_MASTER", "true").lower() == "true",
    "embeddings":   os.getenv("EMBEDDINGS_REQUIRES_MASTER", "true").lower() == "true",
    "ps":           os.getenv("PS_REQUIRES_MASTER", "true").lower() == "true",
}

#! very basic: we only support forcing the model for generate and chat routes - other endpoints will ignore this setting
FORCE_MODEL = os.getenv("FORCE_MODEL", None) # Optional: Force model to be set in the request
if FORCE_MODEL == "": FORCE_MODEL = None


#* Initialize Flask app
app = Flask(__name__)
app.config["DEBUG"] = DEBUG

#* Basic auth check for incoming requests
def check_auth(request, require_master=False):
    try:
        token = request.headers.get("Authorization") 
        if token is None:
            if DEBUG: print("No Authorization header found")
            return False
        
        token = token.split("Bearer ")[1]
        allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._!?@"
        if not all(c in allowed_chars for c in token):
            if DEBUG: print("Invalid token format. Only alphanumeric characters and -._!?@ are allowed.")
            return False
        
    except:
        if DEBUG: print("Unknown Authorization Error")
        return False
        
    if require_master:
        if MASTER_TOKEN is None:
            if DEBUG: print("Warning: Master token not set. Access to this endpoint is disabled.")
            return False
        return (token == MASTER_TOKEN)
    else:
        return (token == AUTH_TOKEN) or (MASTER_TOKEN and token == MASTER_TOKEN)
    

#* --------------------------- Default Routes ---------------------------

@app.route("/api/<slug>", methods=["POST"])
def ollamaproxy(slug):
    if slug not in ENDPOINTS.keys():
        return jsonify({"error": "Unknown endpoint"}), 404
    
    if check_auth(request, require_master=ENDPOINTS[slug]) is False:
        if DEBUG: print("Unauthorized request:", request)
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        if FORCE_MODEL is not None and slug in ["generate", "chat"]:
            # set the model in the request with the forced model
            request.json["model"] = FORCE_MODEL
    except Exception as e:
        print("Error setting forced model:", e)
        return jsonify({"error": "Internal server error"}), 500
    
    try:
        response = requests.post(f"{PROTOCOL}://{OLLAMA_HOST}:{FORWARD_PORT}/api/{slug}", json=request.json)
        return (response.content, response.status_code, response.headers.items())
    except Exception as e:
        print("Error forwarding request:", e)
        return jsonify({"error": "Internal server error"}), 500


#* Development Server 

if __name__ == "__main__":
    print("Running OllamaProxy on port", LISTEN_PORT)
    app.run(host="0.0.0.0", port=LISTEN_PORT)
