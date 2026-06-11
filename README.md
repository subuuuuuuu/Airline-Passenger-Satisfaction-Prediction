# AeroPredict: Airline Passenger Satisfaction Prediction

A modular, production-ready machine learning pipeline and a premium web-based GUI dashboard built to predict airline passenger satisfaction based on demographic, flight distance, delay, and service rating parameters.

## 🚀 Quick Start (Windows)

1. Double-click the **`run.bat`** file.
2. The script will automatically:
   * Setup a local Python virtual environment (`.venv`).
   * Install all required dependencies from `requirements.txt`.
   * Start the local Flask web server.
3. Open your browser and navigate to: **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**

---

## 📁 Project Structure

The project has been organized from a flat Jupyter notebook into the following professional, human-designed structure:

```text
├── config/
│   └── config.yaml               # Centralized configuration for all modules
├── data/
│   ├── raw/                      # Original raw dataset (train.csv)
│   └── processed/                # Split and stratified train/test CSVs
├── models/                       # Saved artifacts (scalers, encoders, model)
│   ├── encoder.pkl               # Fitted Categorical OneHotEncoder
│   ├── imputer.pkl               # Fitted Missing Value Imputer
│   ├── scaler.pkl                # Fitted StandardScaler
│   └── random_forest_model.pkl   # Fitted RandomForest model (GridSearchCV output)
├── notebooks/                    # Archived Jupyter research notebooks
│   └── airline-passenger-satisfaction.ipynb
├── reports/                      # Visualizations and performance summaries
│   ├── metrics.json              # Model evaluation metrics JSON
│   └── confusion_matrix.png      # Confusion Matrix plot
├── src/                          # Modular Python source packages
│   ├── utils.py                  # YAML configuration loader
│   ├── data_ingestion.py         # Data loading and stratified split
│   ├── preprocessing.py          # Data cleaning, Z-score / outlier filtering
│   ├── feature_engineering.py    # Target mapping, One-Hot Encoding, scaling
│   ├── model_training.py         # RandomForest hyperparameter grid search
│   ├── evaluation.py             # Performance metric generation & plotting
│   └── pipeline.py               # End-to-end orchestrator pipeline
├── static/                       # Frontend dashboard files
│   ├── index.html                # Main page dashboard structure
│   ├── style.css                 # Dark-mode styling with glassmorphic cards
│   └── script.js                 # Frontend control script and API fetches
├── app.py                        # Flask backend server exposing API endpoints
├── main.py                       # CLI execution entry point for retraining
├── requirements.txt              # Project package dependencies
└── run.bat                       # Startup script for environment and GUI
```

---

## 📊 Model Performance

Optimized using **GridSearchCV** with 3-fold cross-validation on a dataset of **103,904** passengers, the model scores highly on the unseen test dataset:

* **Accuracy:** `96.33%`
* **Precision:** `96.95%`
* **Recall:** `94.51%`
* **F1-Score:** `95.72%`

---

## 🔧 Modular ML Pipeline Components

* **Config Driven:** Any preprocessing limits, paths, hyperparameter grids, or column classifications are managed via `config/config.yaml`.
* **Robust Preprocessing:** Handles missing values and filters outliers automatically during training, whilst keeping test preprocessing leak-free (no test outliers removed, imputer/scaler are strictly fitted on training splits only).
* **GUI API Endpoints:**
  * **`POST /api/predict`**: Predicts satisfaction for a single passenger.
  * **`POST /api/predict_bulk`**: Processes an uploaded CSV file, adds predicted classes/probabilities, and streams it back to the client as a download.
  * **`GET /api/metrics`**: Serves model metrics in JSON.
  * **`GET /reports/confusion_matrix.png`**: Serves the confusion matrix visual.
