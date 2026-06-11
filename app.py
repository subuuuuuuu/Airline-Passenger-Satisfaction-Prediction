import os
import pickle
import json
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory, Response
from src.utils import load_config
from src.preprocessing import preprocess_data
from src.feature_engineering import transform_features

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='')

# Load configuration and models
CONFIG_PATH = "config/config.yaml"
config = load_config(CONFIG_PATH)

MODEL_PATH = config["model"]["model_path"]
model = None

def load_model_file():
    global model
    if model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Trained model file not found at {MODEL_PATH}. Please train the model first.")
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)

# Route to serve the frontend single page app
@app.route("/")
def index():
    return send_from_directory('static', 'index.html')

# Serve static reports files (specifically confusion_matrix.png)
@app.route("/reports/<path:filename>")
def serve_report(filename):
    return send_from_directory('reports', filename)

# Endpoint for single prediction
@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        load_model_file()
        data = request.json
        if not data:
            return jsonify({"error": "No input data provided"}), 400
        
        # Convert dictionary to DataFrame
        df = pd.DataFrame([data])
        
        # Preprocess and engineer features using standard pipeline modules
        df_clean = preprocess_data(df, config_path=CONFIG_PATH, is_train=False)
        X, _ = transform_features(df_clean, config_path=CONFIG_PATH)
        
        # Make predictions
        prediction = model.predict(X)[0]
        probabilities = model.predict_proba(X)[0]
        
        # Get target mapping
        target_map = config["features"]["target_mapping"]
        # Invert target mapping to get label text: {0: 'neutral or dissatisfied', 1: 'satisfied'}
        inv_target_map = {v: k for k, v in target_map.items()}
        prediction_label = inv_target_map.get(int(prediction), "unknown")
        
        response = {
            "prediction": int(prediction),
            "prediction_label": prediction_label,
            "probability_satisfied": float(probabilities[target_map["satisfied"]]),
            "probability_dissatisfied": float(probabilities[target_map["neutral or dissatisfied"]])
        }
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint for bulk CSV prediction and download
@app.route("/api/predict_bulk", methods=["POST"])
def predict_bulk():
    try:
        load_model_file()
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        if not file.filename.endswith('.csv'):
            return jsonify({"error": "Only CSV files are allowed"}), 400
            
        # Read the uploaded CSV
        df_original = pd.read_csv(file)
        df_to_predict = df_original.copy()
        
        # Check that we have the necessary features
        required_features = config["features"]["numerical_columns"] + config["features"]["categorical_columns"]
        missing_features = [col for col in required_features if col not in df_to_predict.columns]
        if missing_features:
            return jsonify({"error": f"Uploaded CSV is missing required columns: {missing_features}"}), 400
            
        # Preprocess and engineer features
        df_clean = preprocess_data(df_to_predict, config_path=CONFIG_PATH, is_train=False)
        X, _ = transform_features(df_clean, config_path=CONFIG_PATH)
        
        # Make predictions
        predictions = model.predict(X)
        probabilities = model.predict_proba(X)[:, 1] # Probability of being satisfied
        
        # Map predictions back to labels
        target_map = config["features"]["target_mapping"]
        inv_target_map = {v: k for k, v in target_map.items()}
        
        # Align indexes of X and original dataframe, since preprocessing might drop rows if target had nulls
        # (Though during test inference we shouldn't drop rows. In our transform_features it only drops rows
        # if the target satisfaction column was present and has nulls.
        # If satisfaction column is present in bulk uploaded CSV, we alignment matches X.index)
        prediction_labels = [inv_target_map.get(int(pred), "unknown") for pred in predictions]
        
        # Append outputs to a new dataframe
        df_result = df_original.loc[X.index].copy()
        df_result["predicted_satisfaction"] = prediction_labels
        df_result["satisfaction_probability"] = probabilities
        
        # Generate CSV string
        csv_data = df_result.to_csv(index=False)
        
        # Return CSV response
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=predicted_satisfaction_results.csv"}
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to serve metrics json
@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    metrics_path = config["reports"]["metrics_path"]
    if not os.path.exists(metrics_path):
        return jsonify({"error": "Metrics file not found. Train the model first."}), 404
        
    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)
    return jsonify(metrics)

if __name__ == "__main__":
    # Ensure static directory exists
    os.makedirs('static', exist_ok=True)
    
    print("[Server] Starting Flask application...")
    app.run(host="127.0.0.1", port=5000, debug=True)
