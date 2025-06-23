# HomeAssistantLLM

A local voice assistant that integrates with [Home Assistant](https://www.home-assistant.io/) using a language model (LLM) and the Model Context Protocol (MCP). The assistant runs fully offline, utilizing wake-word detection, automatic speech recognition (ASR), and local language model inference.

## Features

- **Wake Word Detection** using Porcupine (e.g., "Jarvis")
- **Voice Activity Detection (VAD)** with Silero VAD
- **Automatic Speech Recognition (ASR)** using Faster Whisper
- **Natural Language Understanding (NLU)** with LangGraph + LLM (Ollama)
- **Command execution** through Home Assistant via REST API
- **Speech synthesis** (TTS) using `pyttsx3`

## Architecture

```
User Speech
   ↓
VoiceAgent (Wakeword + VAD + Whisper)
   ↓
LLM Agent (LangGraph + MCP)
   ↓
Home Assistant Tool Calls
   ↓
Home Assistant REST API
```

## Setup Instructions

1. **Clone the repository**
```bash
git clone https://gitlab.com/your-user/homeassistantllm.git
cd homeassistantllm
```

2. **Create and activate a virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
Create a `.env` file in the root directory with the following:
```env
HASS_URL=http://localhost:8123
HASS_TOKEN=your_home_assistant_long_lived_access_token
```

## Usage

Run the Voice Agent:
```bash
python mcp/Client/voiceAgent.py
```

After saying the hotword (e.g. "Jarvis"), speak a command like:
> "Turn on the lights in the kitchen."

The LLM will interpret the command, and the appropriate tool will be invoked on Home Assistant.

## Configuration

- MCP tool definitions are in `mcp/Server/mcpServer.py`
- Room name translation is handled in a dictionary (`ROOM_NAME_MAP`)
- Default language model: `llama3.1` via Ollama (can be changed in `voiceAgent.py`)

## Dependencies

- `pvporcupine`
- `faster-whisper`
- `sounddevice`
- `scipy`, `numpy`, `torch`, `torchaudio`
- `pyttsx3`
- `langgraph`, `langchain_ollama`, `langchain_mcp_adapters`
- `python-dotenv`

## License

MIT License

Copyright (c) [2025] [Hendrik Hartmann]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
---

**Note**: This project is a local-first assistant prototype and does not require any cloud-based inference. Ideal for privacy-focused smart home users.

