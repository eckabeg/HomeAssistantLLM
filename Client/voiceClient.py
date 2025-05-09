import requests
import sounddevice as sd
import scipy.io.wavfile as wav
import tempfile
import os
import json
import re
from faster_whisper import WhisperModel
from pydub import AudioSegment

# Config
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "llama3.1"
HASS_URL = "http://192.168.178.29:8123"
HASS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI4Yzg3NmE3ZWJmOWU0ZDc2YTkxMDg5OTZlYjNlOWYxNSIsImlhdCI6MTc0Njc4MTU3NCwiZXhwIjoyMDYyMTQxNTc0fQ.odURYTbRy1aU1GmUqZgUET_lNhX4rUSeUYjHBD1qZVM"

HEADERS = {
    "Authorization": f"Bearer {HASS_TOKEN}",
    "Content-Type": "application/json"
}

whisper_model = WhisperModel("medium", compute_type="int8", device="cpu")

def record_audio(duration=5, samplerate=16000):
    print("🎙️ Recording...")
    audio = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        wav.write(f.name, samplerate, audio)
        return f.name

def preprocess_audio(file_path):
    sound = AudioSegment.from_file(file_path)
    sound = sound.set_channels(1).set_frame_rate(16000)
    processed_path = file_path.replace(".wav", "_processed.wav")
    sound.export(processed_path, format="wav")
    return processed_path

def transcribe_audio(file_path):
    processed_path = preprocess_audio(file_path)
    segments, _ = whisper_model.transcribe(processed_path, task="translate")
    os.remove(processed_path)
    return " ".join([s.text.strip() for s in segments])

def ask_ollama(transcript):
    prompt = f"""
You are a Home Assistant automation assistant.
Convert the following user command into a JSON instruction with keys:
"action", "domain", "entity_id", and if needed "temperature".

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

def send_to_home_assistant(command):
    domain = command.get("domain")
    action = command.get("action")
    entity_id = command.get("entity_id")
    if not (domain and action and entity_id):
        print("❌ Invalid command format:", command)
        return

    url = f"{HASS_URL}/api/services/{domain}/{action}"
    payload = { "entity_id": entity_id }

    if domain == "climate" and action == "set_temperature":
        payload["temperature"] = command.get("temperature", 21)

    r = requests.post(url, headers=HEADERS, json=payload)
    print(f"✅ Sent {action} to {entity_id}: {r.status_code}")
    if not r.ok:
        print("❌ Error:", r.text)

def main():
    audio_file = record_audio()
    try:
        text = transcribe_audio(audio_file)
        print(f"📝 Transcript: {text}")
        command = ask_ollama(text)
        if command:
            print(f"🧠 Parsed Command: {command}")
            send_to_home_assistant(command)
    finally:
        os.remove(audio_file)

if __name__ == "__main__":
    main()
