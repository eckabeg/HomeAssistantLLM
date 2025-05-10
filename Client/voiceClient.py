import socket
import json
import whisper
import sounddevice as sd
import numpy as np
import tempfile
import scipy.io.wavfile as wavfile
import pyttsx3

HOST = '127.0.0.1'
PORT = 65435
model = whisper.load_model("medium")  # or "tiny", "small", "medium", "large"

def record_audio(duration=8, samplerate=16000):
    print(f"[Voice] Recording for {duration} seconds...")
    audio = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    return audio, samplerate

def transcribe_audio(audio_data, samplerate):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wavfile.write(f.name, samplerate, audio_data)
        result = model.transcribe(f.name)
    return result["text"]

def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 170)  # Optional: adjust speaking speed
    engine.say(text)
    engine.runAndWait()

while True:
    input("[Press Enter to Speak]")
    audio_data, sr = record_audio()
    user_text = transcribe_audio(audio_data, sr)
    print(f"You said: {user_text}")

    if user_text.lower() in ["exit", "quit"]:
        break

    data = {
        "message": user_text
    }

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(json.dumps(data).encode())
        response = s.recv(4096)

    result = json.loads(response.decode())
    response_text = result.get("response", "Sorry, I didn’t understand that.")
    print(f"Assistant: {result['response']}")
    speak(response_text)
