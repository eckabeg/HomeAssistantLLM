import asyncio
import time

import numpy as np
import pvporcupine
import pyttsx3
import scipy.io.wavfile as wavfile
import sounddevice as sd
import torchaudio
import torch
from faster_whisper import WhisperModel
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
import soundfile

# === CONFIG ===
ACCESS_KEY = ""
HOTWORD = "jarvis"
MCP_NAMESPACE = "HomeAssistant"
SAMPLERATE = 16000
CHANNELS = 1

# VAD-Modell laden (Silero VAD)
model, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad',
    force_reload=False,
    trust_repo=True
)
get_speech_ts = utils[0]
read_audio   = utils[2]

# === Setup Porcupine (Hotword) ===
porcupine = pvporcupine.create(access_key=ACCESS_KEY, keywords=[HOTWORD])

# === TTS (pyttsx3) ===
tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 170)

whisper_model = WhisperModel("medium", device="cpu")

def speak(text: str):
    """
    Gibt den Text per Konsole und via TTS aus.
    """
    print(f"Assistant: {text}")
    tts_engine.say(text)
    tts_engine.runAndWait()


# === Hotword Detection ===
def listen_for_hotword():
    """
    Wartet, bis das konfigurierten Hotword (z. B. "jarvis") erkannt wird.
    Bricht dann ab (Callback-Abort) und kehrt zurück.
    """
    frame_len = porcupine.frame_length
    hotword_detected = False

    def callback(indata, frames, time_info, status):
        # Porcupine erwartet 16-bit PCM-Samples
        nonlocal hotword_detected
        pcm = np.frombuffer(indata, dtype=np.int16)
        keyword_index = porcupine.process(pcm)
        if keyword_index >= 0:
            print("Hotword erkannt!")
            hotword_detected = True

    with sd.RawInputStream(
        samplerate=porcupine.sample_rate,
        blocksize=frame_len,
        dtype='int16',
        channels=CHANNELS,
        callback=callback
    ):
        print("Warte auf Wake Word …")
        while not hotword_detected:
            time.sleep(0.1)  # keep loop alive

# === Voice Recording mit VAD ===
def record_until_silence(filename="voice_command.wav", timeout=3, threshold_sec=1.5):
    """
    Nimmt Sprachdaten auf (BIS timeout erreicht ist).
    Speichert in WAV, führt per Silero VAD eine Prüfung durch und
    gibt den Dateinamen zurück, falls Sprachaktivität erkannt wurde.
    """
    print("Aufnahme gestartet. Bitte sprechen …")
    audio_frames = []
    start_time = time.time()

    with sd.InputStream(samplerate=SAMPLERATE, channels=CHANNELS, dtype='int16') as stream:
        while True:
            audio_block, _ = stream.read(int(SAMPLERATE * 0.1))
            audio_frames.append(audio_block[:, 0].copy())

            # Abbruch, wenn timeout überschritten ist
            if time.time() - start_time > timeout:
                break

    audio_np = np.concatenate(audio_frames)
    wavfile.write(filename, SAMPLERATE, audio_np)

    # VAD prüfen
    wav = read_audio(filename, sampling_rate=SAMPLERATE)
    speech_ts = get_speech_ts(wav, model, sampling_rate=SAMPLERATE)

    if speech_ts:
        print("Sprachaktivität erkannt.")
        return filename
    else:
        print("Keine Sprache erkannt. Versuche erneut …")
        return None


# === Whisper Transkription (lokal) ===
def transcribe_local_whisper(filepath):
    """
    Nutzt Whisper (lokal) um die WAV-Datei zu transkribieren.
    """
    segments, _ = whisper_model.transcribe(filepath)
    text = " ".join(segment.text for segment in segments)
    print("Erkannt (Whisper):", text)
    return text


# === MCP-Agent initialisieren (async) ===
async def init_agent():
    """
    Bringt den MCP-Client mit deinem Home Assistant-Server zum Laufen und
    erstellt den ReAct-Agenten mit ChatOllama + HA-Tools.
    """
    client = MultiServerMCPClient({
        "HomeAssistant": {
            "command": "python",
            "args": ["./../Server/mcpServer.py"],
            "transport": "stdio",
        }
    })

    tools = await client.get_tools()

    llm = ChatOllama(
        model="llama3.1",  # ggf. llama3.1:7b o. Ä., je nachdem, was gepullt wurde
        base_url="http://127.0.0.1:11434"
    )

    agent_new = create_react_agent(llm, tools)
    return agent_new


# === Haupt-Loop (synchron) ===
async def main_loop(agent):
    """
    Endlosschleife:
      1) Warte auf das Hotword
      2) Aufnahme via VAD
      3) Transkription
      4) Sende Prompt an Agent (agent.ainvoke)
      5) Sprachausgabe der Antwort
    """
    while True:
        try:
            # 1) Hotword erkennen
            listen_for_hotword()

            # 2) Aufnehmen (bis timeout)
            filepath = None
            while filepath is None:
                filepath = record_until_silence(timeout=2, threshold_sec=1.5)

            # 3) Transkribieren
            transcript = transcribe_local_whisper(filepath)

            # 4) Anfrage an den MCP-Agenten
            #    Wir übermitteln die transkribierte Nutzernachricht
            response = await agent.ainvoke({
                "messages": [{"role": "user", "content": transcript}]
            })
            last_msg = response["messages"][-1]  # AIMessage
            answer = last_msg.content
            print(answer)
            # 5) TTS-Ausgabe
            #speak(answer)

        except KeyboardInterrupt:
            print("Beende Voice-Client.")
            break
        except Exception as e:
            print("Fehler im Hauptloop:", e)
            # Bei einem Fehler einfach zum nächsten Hotword zurückkehren
            continue


if __name__ == "__main__":
    print("=== MCP-Voice-Client Started ===")

    # Agent asynchron initialisieren
    agent = asyncio.run(init_agent())

    # Synchronen Haupt-Loop starten
    asyncio.run(main_loop(agent))
