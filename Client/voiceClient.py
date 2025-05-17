import pvporcupine
import sounddevice as sd
import numpy as np
import struct
import queue
import time
import requests
import scipy.io.wavfile as wavfile
import pyttsx3
import torch
from silero_vad import VoiceActivityDetector

# === CONFIG ===
ACCESS_KEY = "xFRSB4+mC1Fp6Hwh3+u+cg5VZqLXP+jpfl8qN/P7C8c0MlJmIy5ACg=="
HOTWORD = "jarvis"
MCP_SERVER = "http://127.0.0.1:65432"
SAMPLERATE = 16000
CHANNELS = 1

# === Setup ===
porcupine = pvporcupine.create(access_key=ACCESS_KEY, keywords=[HOTWORD])
vad = VoiceActivityDetector("cpu")
tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 170)

# === TTS ===
def speak(text):
    print(f"Assistant: {text}")
    tts_engine.say(text)
    tts_engine.runAndWait()

# === Hotword Detection ===
def listen_for_hotword():
    frame_len = porcupine.frame_length

    def callback(indata, frames, time, status):
        pcm = struct.unpack_from("h" * len(indata), indata)
        keyword_index = porcupine.process(pcm)
        if keyword_index >= 0:
            print("✅ Hotword detected!")
            raise sd.CallbackAbort

    with sd.RawInputStream(
        samplerate=porcupine.sample_rate,
        blocksize=frame_len,
        dtype='int16',
        channels=CHANNELS,
        callback=callback
    ):
        print("🎙 Waiting for wake word...")
        while True:
            pass

# === Voice Recording with VAD ===
def record_with_vad(filename="voice_command.wav", timeout=1.5):
    print("🎤 Listening...")
    audio = []
    silence_timer = 0

    with sd.InputStream(samplerate=SAMPLERATE, channels=CHANNELS, dtype='int16') as stream:
        while True:
            frame, _ = stream.read(512)
            np_frame = np.frombuffer(frame, dtype=np.int16)
            audio.append(np_frame)

            if vad(np_frame, SAMPLERATE):
                silence_timer = 0
            else:
                silence_timer += 512 / SAMPLERATE

            if silence_timer > timeout:
                print("🛑 Silence detected. Stopping.")
                break

    audio_np = np.concatenate(audio)
    wavfile.write(filename, SAMPLERATE, audio_np)
    return filename

# === Whisper Transcription (via remote or local model) ===
def transcribe_local_whisper(filepath):
    import whisper
    model = whisper.load_model("medium")  # or use "small", "medium", etc.
    result = model.transcribe(filepath)
    print("You said:", result["text"])
    return result["text"]

# === Send to MCP server ===
def send_to_mcp(transcript):
    payload = {
        "user": "voice_user",
        "message": transcript
    }
    try:
        response = requests.post(MCP_SERVER, json=payload)
        if response.ok:
            result = response.json()
            speak(result.get("response", "Done."))
        else:
            speak("Something went wrong.")
    except Exception as e:
        print("❌ MCP error:", e)
        speak("I couldn't reach the server.")

# === Main Loop ===
def main():
    print("=== MCP Voice Client Started ===")
    while True:
        try:
            listen_for_hotword()
            filepath = record_with_vad()
            transcript = transcribe_local_whisper(filepath)
            send_to_mcp(transcript)
        except KeyboardInterrupt:
            print("Exiting.")
            break
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    main()
