import requests
import sounddevice as sd
import scipy.io.wavfile as wav
import tempfile
import os
from faster_whisper import WhisperModel
import re

# Home Assistant config
HASS_URL = "http://homeassistant.local:8123"
HASS_TOKEN = "your_long_lived_token_here"
HEADERS = {
    "Authorization": f"Bearer {HASS_TOKEN}",
    "Content-Type": "application/json"
}

# Whisper model (fast and small)
model = WhisperModel("base", compute_type="int8")

def record_audio(duration=5, samplerate=16000):
    print("Recording...")
    audio = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        wav.write(f.name, samplerate, audio)
        return f.name

def transcribe(file_path):
    segments, _ = model.transcribe(file_path)
    return " ".join([s.text for s in segments])

def get_all_entities():
    response = requests.get(f"{HASS_URL}/api/states", headers=HEADERS)
    return response.json()

def normalize_name(name):
    return name.lower().replace("_", " ").replace(".", " ").replace("light", "").strip()

def find_matching_entity(transcript, entities):
    for entity in entities:
        eid = entity['entity_id']
        name = normalize_name(eid)
        if name in transcript:
            domain = eid.split(".")[0]
            return domain, eid
    return None, None

def control_entity(domain, entity_id, action):
    service_map = {
        "on": "turn_on",
        "off": "turn_off",
        "open": "open_cover",
        "close": "close_cover"
    }
    service = service_map.get(action)
    if not service:
        print("Unknown action")
        return
    url = f"{HASS_URL}/api/services/{domain}/{service}"
    data = { "entity_id": entity_id }
    r = requests.post(url, headers=HEADERS, json=data)
    print(f"{action.upper()} {entity_id}: {r.status_code}")

def parse_command(text):
    if "turn on" in text:
        return "on"
    elif "turn off" in text:
        return "off"
    elif "open" in text:
        return "open"
    elif "close" in text:
        return "close"
    else:
        return None

def main():
    entities = get_all_entities()
    audio_file = record_audio()
    text = transcribe(audio_file).lower()
    os.remove(audio_file)

    print(f"Transcript: {text}")
    action = parse_command(text)
    if not action:
        print("No action detected.")
        return

    domain, entity_id = find_matching_entity(text, entities)
    if not entity_id:
        print("No matching entity found.")
        return

    control_entity(domain, entity_id, action)

if __name__ == "__main__":
    main()
