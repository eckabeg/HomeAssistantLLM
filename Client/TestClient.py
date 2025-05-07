import socket
import json

msg = {
    "model_key": "llama4",  # or "mistral", "gemma", etc.
    "prompt": "Explain photosynthesis in 2 sentences."
}

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(("127.0.0.1", 9000))
    s.sendall(json.dumps(msg).encode("utf-8"))
    response = s.recv(8192)

print("Response:", response.decode("utf-8"))
