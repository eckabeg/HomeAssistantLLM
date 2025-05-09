import requests
import json
import re

# Config
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "llama3.1"

HASS_URL = "http://192.168.178.29:8123"
HASS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI4Yzg3NmE3ZWJmOWU0ZDc2YTkxMDg5OTZlYjNlOWYxNSIsImlhdCI6MTc0Njc4MTU3NCwiZXhwIjoyMDYyMTQxNTc0fQ.odURYTbRy1aU1GmUqZgUET_lNhX4rUSeUYjHBD1qZVM"

HEADERS = {
    "Authorization": f"Bearer {HASS_TOKEN}",
    "Content-Type": "application/json"
}

def ask_ollama(user_input):
    prompt = f"""
You are a Home Assistant automation assistant.
Convert the following user command into a JSON instruction with keys:
"action", "domain", "entity_id", and if needed "temperature".

Example:
Input: "Turn off the kitchen light"
Output: {{ "action": "turn_off", "domain": "light", "entity_id": "light.room}}
Output: {{ "action": "set_temperature", "domain": "climate", "entity_id": "climate.thermostat_room_side", "temperature": 21" }}

Input: "{user_input}"
Output:
"""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        raw = response.json().get("response", "")

        # Extract first valid JSON object from raw output
        json_match = re.search(r'{.*}', raw, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        else:
            print("⚠️ No JSON found in Ollama response.")
            print("🧠 Raw output:", raw)
            return None
    except Exception as e:
        print("❌ Error talking to Ollama:", e)
        return None

def send_to_home_assistant(command):
    domain = command.get("domain")
    action = command.get("action")
    entity_id = command.get("entity_id")
    if not all([domain, action, entity_id]):
        print("❌ Incomplete command:", command)
        return

    url = f"{HASS_URL}/api/services/{domain}/{action}"
    payload = { "entity_id": entity_id }

    if domain == "climate" and action == "set_temperature":
        payload["temperature"] = command.get("temperature", 21)

    r = requests.post(url, headers=HEADERS, json=payload)
    if r.ok:
        print(f"✅ Executed: {action} → {entity_id}")
    else:
        print("❌ Failed:", r.text)

def main():
    while True:
        user_input = input("💬 Command (or 'exit'): ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break

        command = ask_ollama(user_input)
        if command:
            print("🧠 Parsed Command:", command)
            send_to_home_assistant(command)

if __name__ == "__main__":
    main()
