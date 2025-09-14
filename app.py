# app.py - wastesense backend (safe version)
import os
import io
import json
import logging
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import numpy as np
import tensorflow as tf

# optional huggingface helper (import only if used)
HF_ENABLED = False
HF_REPO_ID = os.environ.get("HF_REPO_ID")  # optional: "username/repo" to download model at startup
try:
    if HF_REPO_ID:
        from huggingface_hub import hf_hub_download
        HF_ENABLED = True
except Exception:
    HF_ENABLED = False

app = Flask(__name__)
CORS(app)

# Limit upload size (50 MB)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wastesense-backend")

# ---------- CONFIG ----------
MODEL_CANDIDATES = [
    "wastesense_model.keras",
    "wastesense_model_archive.zip",
    "best_model.h5",
    "wastesense_final.h5",
    "model.h5"
]

LABELS_FILE = "labels.json"
DEFAULT_CLASS_NAMES = ['Battery', 'Plastic', 'E-Waste', 'Organic', 'Metal', 'Glass']
INPUT_SIZE_DEFAULT = (224, 224)
# ----------------------------

def find_model_path():
    # If huggingface requested, try to download
    if HF_ENABLED:
        try:
            logger.info("HF repo specified; attempting to download wastesense_model.keras and labels.json from Hugging Face...")
            # attempt to download wastesense_model.keras and labels.json
            try:
                model_file = hf_hub_download(repo_id=HF_REPO_ID, filename="wastesense_model.keras")
                logger.info("Downloaded model from HF: %s", model_file)
            except Exception as ex:
                logger.warning("Could not download wastesense_model.keras from HF: %s", ex)
                model_file = None
            try:
                labels_file = hf_hub_download(repo_id=HF_REPO_ID, filename="labels.json")
                logger.info("Downloaded labels.json from HF: %s", labels_file)
            except Exception as ex:
                logger.warning("Could not download labels.json from HF: %s", ex)
                labels_file = None
            if model_file and os.path.exists(model_file):
                return model_file
        except Exception as e:
            logger.warning("HF download flow failed: %s", e)

    for p in MODEL_CANDIDATES:
        if os.path.exists(p):
            return p
    return None

logger.info("🔎 Looking for model file...")
model_path = find_model_path()
if not model_path:
    raise FileNotFoundError(f"No model found. Place one of {MODEL_CANDIDATES} next to app.py or set HF_REPO_ID env var to download from Hugging Face.")

logger.info(f"🧠 Loading model from: {model_path}")
# load model (non-compiled)
model = tf.keras.models.load_model(model_path, compile=False)
logger.info("✅ Model loaded.")

# try to load labels
if os.path.exists(LABELS_FILE):
    try:
        with open(LABELS_FILE, "r") as f:
            class_names = json.load(f)
        logger.info("✅ Loaded class names from %s", LABELS_FILE)
    except Exception as e:
        logger.warning("⚠️ Failed to load labels.json: %s", e)
        class_names = DEFAULT_CLASS_NAMES
else:
    class_names = DEFAULT_CLASS_NAMES
    logger.warning("⚠️ labels.json not found. Using DEFAULT_CLASS_NAMES. Make sure order matches model output!")

# infer input size
try:
    shape = model.inputs[0].shape.as_list()
    if len(shape) >= 3 and shape[1] and shape[2]:
        INPUT_SIZE = (int(shape[1]), int(shape[2]))
    else:
        INPUT_SIZE = INPUT_SIZE_DEFAULT
except Exception:
    INPUT_SIZE = INPUT_SIZE_DEFAULT

logger.info("Model expects input size: %s", INPUT_SIZE)
# choose a preprocess fn that matches your training head
preprocess_fn = tf.keras.applications.efficientnet.preprocess_input

# impact_map (same as you had)
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

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "wastesense-backend", "model_loaded_from": model_path})

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
                return jsonify({'error': 'No image provided. Send multipart form-data "image" file or JSON {"image": "<base64>"}'}), 400
            b64 = data['image']
            if ',' in b64:
                b64 = b64.split(',',1)[1]
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
        logger.info("[PREDICT] %s %.3f", pred_class, confidence)
        return jsonify(response)
    except Exception as e:
        logger.exception("Error in /predict:")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    # run locally for testing
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
