def load_model(model_key):
    if model_key in loaded_models:
        return loaded_models[model_key]
    if model_key not in MODEL_REGISTRY:
        raise ValueError("Model not found")
    model_path = MODEL_REGISTRY[model_key]
    model = joblib.load(model_path)
    loaded_models[model_key] = model
    return model

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    model_key = data.get("model_key")
    features = data.get("features")

    try:
        model = load_model(model_key)
        prediction = model.predict([features])
        return jsonify({"prediction": prediction.tolist()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=8000)