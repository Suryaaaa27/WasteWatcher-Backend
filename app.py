# app.py - updated for Hugging Face hosted model + Render deployment
import os
import io
import json
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
import tensorflow as tf
from huggingface_hub import hf_hub_download

app = Flask(__name__)
CORS(app)  # allow frontend to call this API

# ---------- CONFIG ----------
MODEL_REPO = "SuryaaaaSnehaaaa/wastewatcher"   # your Hugging Face repo
MODEL_FILE = "wastesense_model.keras"
LABELS_FILE = "labels.json"
DEFAULT_CLASS_NAMES = ['Battery', 'Plastic', 'E-Waste', 'Organic', 'Metal', 'Glass']
INPUT_SIZE_DEFAULT = (224, 224)
# ----------------------------

print("🔎 Downloading model + labels from Hugging Face Hub...")

try:
    model_path = hf_hub_download(repo_id=MODEL_REPO, filename=MODEL_FILE)
except Exception as e:
    raise RuntimeError(f"❌ Could not download model from Hugging Face: {e}")

try:
    labels_path = hf_hub_download(repo_id=MODEL_REPO, filename=LABELS_FILE)
except Exception:
    labels_path = None

print(f"🧠 Loading model from: {model_path}")
model = tf.keras.models.load_model(model_path, compile=False)
print("✅ Model loaded.")

# try to load labels.json
if labels_path and os.path.exists(labels_path):
    try:
        with open(labels_path, "r") as f:
            class_names = json.load(f)
        print("✅ Loaded class names from", LABELS_FILE)
    except Exception as e:
        print("⚠️ Failed to load labels.json:", e)
        class_names = DEFAULT_CLASS_NAMES
else:
    class_names = DEFAULT_CLASS_NAMES
    print("⚠️ labels.json not found. Using DEFAULT_CLASS_NAMES.")

# determine expected input size
try:
    shape = model.inputs[0].shape.as_list()  # e.g. [None, 224, 224, 3]
    if len(shape) >= 3 and shape[1] and shape[2]:
        INPUT_SIZE = (int(shape[1]), int(shape[2]))
    else:
        INPUT_SIZE = INPUT_SIZE_DEFAULT
except Exception:
    INPUT_SIZE = INPUT_SIZE_DEFAULT

print("Model expects input size:", INPUT_SIZE)
preprocess_fn = tf.keras.applications.efficientnet.preprocess_input

# Impact map
impact_map = {
    'Battery': {'odp_units': 0.002, 'co2_kg': 0.8, 'toxicity': 8, 'action': 'Drop at CECB Hazard Kiosk', 'value': '₹45 cobalt', 'ozone_protection_score': 99.8},
    'Plastic': {'odp_units': 0.0005, 'co2_kg': 3.5, 'toxicity': 5, 'action': 'Recycle at Plastic Collection Point', 'value': '₹12 plastic pellets', 'ozone_protection_score': 99.95},
    'E-Waste': {'odp_units': 0.001, 'co2_kg': 1.2, 'toxicity': 7, 'action': 'Hand over to E-Waste Recycler', 'value': '₹80 copper/gold', 'ozone_protection_score': 99.9},
    'Organic': {'odp_units': 0.0001, 'co2_kg': 0.3, 'toxicity': 2, 'action': 'Compost or Biogas Unit', 'value': 'Free compost', 'ozone_protection_score': 99.99},
    'Metal': {'odp_units': 0.0002, 'co2_kg': 0.9, 'toxicity': 4, 'action': 'Metal Scrap Vendor', 'value': '₹30 scrap metal', 'ozone_protection_score': 99.98},
    'Glass': {'odp_units': 0.0001, 'co2_kg': 0.5, 'toxicity': 3, 'action': 'Glass Recycling Center', 'value': '₹15 glass cullet', 'ozone_protection_score': 99.99}
}

def preprocess_image_file(file_stream):
    img = Image.open(io.BytesIO(file_stream)).convert('RGB')
    img = img.resize(INPUT_SIZE, Image.BICUBIC)
    arr = np.array(img).astype(np.float32)
    arr = preprocess_fn(arr)
    arr = np.expand_dims(arr, axis=0)
    return arr

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'model_loaded_from': model_path, 'input_size': INPUT_SIZE, 'classes': class_names})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'image' in request.files:
            file = request.files['image'].read()
            img_tensor = preprocess_image_file(file)
        else:
            data = request.get_json(force=True, silent=True)
            if not data or ('image' not in data):
                return jsonify({'error': 'No image provided'}), 400
            b64 = data['image']
            if ',' in b64:  # handle data URLs
                b64 = b64.split(',', 1)[1]
            import base64
            file = base64.b64decode(b64)
            img_tensor = preprocess_image_file(file)

        preds = model.predict(img_tensor)
        probs = preds[0].tolist()
        idx = int(np.argmax(probs))
        confidence = float(probs[idx])
        pred_class = class_names[idx] if idx < len(class_names) else f"class_{idx}"

        impact = impact_map.get(pred_class, {'odp_units':0, 'co2_kg':0, 'toxicity':0, 'action':'Unknown', 'value':'0', 'ozone_protection_score':0})

        response = {
            'waste_type': pred_class,
            'confidence': confidence,
            **impact
        }
        print(f"[PREDICT] {pred_class} {confidence:.3f}")
        return jsonify(response)
    except Exception as e:
        print("Error in /predict:", str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
