import socket
import json
import requests

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def query_ollama(model: str, prompt: str, stream: bool = False):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "No response")
    except Exception as e:
        return f"Error querying Ollama: {str(e)}"

def handle_request(request_data: str):
    try:
        req = json.loads(request_data)
        model_key = req.get("model_key", "llama4")
        prompt = req.get("prompt", "Hello!")
        result = query_ollama(model=model_key, prompt=prompt)
        return json.dumps({"response": result})
    except Exception as e:
        return json.dumps({"error": str(e)})

def run_server(host="127.0.0.1", port=9000):
    print(f"Starting TCP MCP server on {host}:{port}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((host, port))
        server.listen()
        while True:
            conn, addr = server.accept()
            with conn:
                print(f"Connected by {addr}")
                try:
                    data = conn.recv(8192)
                    if not data:
                        continue
                    response = handle_request(data.decode("utf-8"))
                    conn.sendall(response.encode("utf-8"))
                except Exception as e:
                    error_msg = json.dumps({"error": str(e)})
                    conn.sendall(error_msg.encode("utf-8"))

if __name__ == "__main__":
    run_server()
