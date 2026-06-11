import os
import pandas as pd
from src.utils import load_config
from src.data_ingestion import ingest_data
from src.preprocessing import preprocess_data
from src.feature_engineering import fit_transform_features, transform_features
from src.model_training import train_model
from src.evaluation import evaluate_model

def run_pipeline(config_path="config/config.yaml"):
    """
    Orchestrates the entire machine learning pipeline end-to-end.
    """
    print("=" * 60)
    print("      STARTING AIRLINE PASSENGER SATISFACTION ML PIPELINE")
    print("=" * 60)
    
    # Load configuration to get paths
    config = load_config(config_path)
    train_csv_path = config["data"]["train_path"]
    test_csv_path = config["data"]["test_path"]
    
    # 1. Ingestion
    print("\n--- STEP 1: DATA INGESTION ---")
    ingest_data(config_path)
    
    # Load ingested split datasets
    train_df = pd.read_csv(train_csv_path)
    test_df = pd.read_csv(test_csv_path)
    
    # 2. Preprocessing
    print("\n--- STEP 2: DATA PREPROCESSING ---")
    print("Preprocessing train set (outlier removal + imputation)...")
    train_clean_df = preprocess_data(train_df, config_path=config_path, is_train=True)
    
    print("\nPreprocessing test set (imputation only)...")
    test_clean_df = preprocess_data(test_df, config_path=config_path, is_train=False)
    
    # 3. Feature Engineering
    print("\n--- STEP 3: FEATURE ENGINEERING ---")
    print("Fitting and transforming train set features...")
    X_train, y_train = fit_transform_features(train_clean_df, config_path=config_path)
    
    print("\nTransforming test set features...")
    X_test, y_test = transform_features(test_clean_df, config_path=config_path)
    
    # 4. Model Training
    print("\n--- STEP 4: MODEL TRAINING & HYPERPARAMETER TUNING ---")
    best_model = train_model(X_train, y_train, config_path=config_path)
    
    # 5. Model Evaluation
    print("\n--- STEP 5: MODEL EVALUATION ---")
    metrics = evaluate_model(X_test, y_test, config_path=config_path)
    
    print("\n" + "=" * 60)
    print("            PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    return metrics

if __name__ == "__main__":
    run_pipeline()
