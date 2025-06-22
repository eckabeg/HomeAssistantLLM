import socket
import json
import requests
import re

# === Configuration ===
HOST = '127.0.0.1'
PORT = 65435
OLLAMA_MODEL = 'llama3.1'
OLLAMA_URL = 'http://127.0.0.1:11434/api/generate'
HASS_URL = "http://192.168.178.29:8123"
HASS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI4Yzg3NmE3ZWJmOWU0ZDc2YTkxMDg5OTZlYjNlOWYxNSIsImlhdCI6MTc0Njc4MTU3NCwiZXhwIjoyMDYyMTQxNTc0fQ.odURYTbRy1aU1GmUqZgUET_lNhX4rUSeUYjHBD1qZVM"

HEADERS = {
    "Authorization": f"Bearer {HASS_TOKEN}",
    "Content-Type": "application/json"
}

# === Ollama LLM Integration ===
def ask_ollama(transcript):
    prompt = f"""
You are a Home Assistant automation assistant.
First, if the input is in German, translate it to English.
Then convert the (translated) user command into a JSON instruction with keys:
"action", "domain", "entity_id", and if needed "temperature".
After that send an answer of what you did to Home Assistant.

Examples:
Input: "Turn off the kitchen light"
Output: {{ "action": "turn_off", "domain": "light", "entity_id": "light.kitchen" }}

Input: "Set the room temperature to 21"
Output: {{ "action": "set_temperature", "domain": "climate", "entity_id": "climate.thermostat_room", "temperature": 21 }}

Input: "{transcript}"
Output:
"""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        result = response.json()
        raw_output = result.get("response", "")
        json_match = re.search(r'{.*}', raw_output, re.DOTALL)
        if json_match:
            clean_json = json_match.group(0)
            return json.loads(clean_json)
        else:
            print("⚠️ No JSON found in model response:", raw_output)
            return None
    except Exception as e:
        print("❌ Error talking to Ollama:", e)
        return None

# === Home Assistant Control ===
def send_to_home_assistant(command):
    domain = command.get("domain")
    action = command.get("action")
    entity_id = command.get("entity_id")
    if not (domain and action and entity_id):
        print("❌ Invalid command format:", command)
        return False, "Invalid format"

    url = f"{HASS_URL}/api/services/{domain}/{action}"
    payload = { "entity_id": entity_id }

    if domain == "climate" and action == "set_temperature":
        payload["temperature"] = command.get("temperature", 21)

    try:
        r = requests.post(url, headers=HEADERS, json=payload)
        print(f"✅ Sent {action} to {entity_id}: {r.status_code}")
        return r.ok, r.text
    except Exception as e:
        print("❌ Error communicating with Home Assistant:", e)
        return False, str(e)

# === Main Handler ===
def handle_request(data):
    user = data.get("user", "default")
    message = data.get("message", "")

    print(f"[MCP] {user} said: {message}")
    command = ask_ollama(message)

    if not command:
        return {
            "response": "Sorry, I couldn't understand your command.",
            "command": None
        }

    success, result = send_to_home_assistant(command)

    return {
        "response": f"✅ Command executed: {command}" if success else "❌ Failed to execute command.",
        "command": command,
        "details": result
    }

# === Server Socket Loop ===
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"[MCP Server] Listening on {HOST}:{PORT} (with Ollama + Home Assistant)")

    while True:
        conn, addr = s.accept()
        with conn:
            data = conn.recv(4096)
            if not data:
                continue
            try:
                request = json.loads(data.decode())
                result = handle_request(request)
                conn.sendall(json.dumps(result).encode())
            except Exception as e:
                error_response = {"error": str(e)}
                conn.sendall(json.dumps(error_response).encode())
