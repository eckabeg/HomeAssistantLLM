import whisper
from flask import Flask, request, jsonify
import tempfile

app = Flask(__name__)
model = whisper.load_model("large")  # or "medium", "base", etc.

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file uploaded'}), 400

    audio_file = request.files['audio']
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp:
        audio_file.save(temp.name)
        result = model.transcribe(temp.name)

    return jsonify({'text': result['text']})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
