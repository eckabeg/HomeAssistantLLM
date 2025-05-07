import socket
import json

def send_model_context(payload: dict, host="127.0.0.1", port=9000) -> dict:
    message = json.dumps(payload)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(message.encode("utf-8"))
        data = s.recv(8192)

    response = json.loads(data.decode("utf-8"))
    if "error" in response:
        raise Exception(response["error"])
    return response
