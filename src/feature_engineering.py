import os
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from src.utils import load_config

def fit_transform_features(df, config_path="config/config.yaml"):
    """
    Fits encoders/scalers on the training dataframe, transforms it,
    and saves the fitted preprocessors to models/ directory.
    """
    config = load_config(config_path)
    
    cat_cols = config["features"]["categorical_columns"]
    num_cols = config["features"]["numerical_columns"]
    target_col = config["features"]["target_column"]
    target_map = config["features"]["target_mapping"]
    
    encoder_path = config["model"]["encoder_path"]
    scaler_path = config["model"]["scaler_path"]
    
    df = df.copy()
    
    # 1. Process target variable (if present)
    y = None
    if target_col in df.columns:
        print(f"[Feature Engineering] Mapping target column '{target_col}'...")
        y = df[target_col].map(target_map)
        
        # Verify if there are unmapped values (e.g. spelling errors or NaN)
        if y.isnull().any():
            unmapped_vals = df[df[target_col].notnull() & y.isnull()][target_col].unique()
            if len(unmapped_vals) > 0:
                print(f"[Feature Engineering] Warning: Unmapped target values found: {unmapped_vals}. Imputing/dropping.")
                y = y.fillna(0).astype(int)  # fallback to majority class or default 0
            else:
                # If target itself had nulls
                print("[Feature Engineering] Target has nulls. Dropping those rows.")
                valid_idx = y.notnull()
                df = df[valid_idx]
                y = y[valid_idx].astype(int)
        else:
            y = y.astype(int)
            
    # 2. Process categorical columns (One-Hot Encoding)
    print(f"[Feature Engineering] Fitting and applying OneHotEncoder on: {cat_cols}")
    encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    encoded_cats = encoder.fit_transform(df[cat_cols])
    encoded_cat_cols = encoder.get_feature_names_out(cat_cols)
    encoded_cats_df = pd.DataFrame(encoded_cats, columns=encoded_cat_cols, index=df.index)
    
    # Save encoder
    os.makedirs(os.path.dirname(encoder_path), exist_ok=True)
    with open(encoder_path, "wb") as f:
        pickle.dump(encoder, f)
    print(f"[Feature Engineering] Saved fitted encoder to {encoder_path}")
    
    # 3. Process numerical columns (Standard Scaling)
    print(f"[Feature Engineering] Fitting and applying StandardScaler on: {num_cols}")
    scaler = StandardScaler()
    scaled_nums = scaler.fit_transform(df[num_cols])
    scaled_nums_df = pd.DataFrame(scaled_nums, columns=num_cols, index=df.index)
    
    # Save scaler
    os.makedirs(os.path.dirname(scaler_path), exist_ok=True)
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)
    print(f"[Feature Engineering] Saved fitted scaler to {scaler_path}")
    
    # 4. Combine encoded and scaled features
    X = pd.concat([scaled_nums_df, encoded_cats_df], axis=1)
    print(f"[Feature Engineering] Final processed feature shape: {X.shape}")
    
    return X, y

def transform_features(df, config_path="config/config.yaml"):
    """
    Transforms testing/inference dataframe using preloaded fitted encoders and scalers.
    """
    config = load_config(config_path)
    
    cat_cols = config["features"]["categorical_columns"]
    num_cols = config["features"]["numerical_columns"]
    target_col = config["features"]["target_column"]
    target_map = config["features"]["target_mapping"]
    
    encoder_path = config["model"]["encoder_path"]
    scaler_path = config["model"]["scaler_path"]
    
    df = df.copy()
    
    # 1. Process target variable (if present)
    y = None
    if target_col in df.columns:
        y = df[target_col].map(target_map)
        if y.isnull().any():
            y = y.fillna(0).astype(int)
        else:
            y = y.astype(int)
            
    # 2. Load and apply OneHotEncoder
    if not os.path.exists(encoder_path):
        raise FileNotFoundError(f"Fitted encoder not found at {encoder_path}. Train the pipeline first.")
        
    with open(encoder_path, "rb") as f:
        encoder = pickle.load(f)
        
    encoded_cats = encoder.transform(df[cat_cols])
    encoded_cat_cols = encoder.get_feature_names_out(cat_cols)
    encoded_cats_df = pd.DataFrame(encoded_cats, columns=encoded_cat_cols, index=df.index)
    
    # 3. Load and apply StandardScaler
    if not os.path.exists(scaler_path):
        raise FileNotFoundError(f"Fitted scaler not found at {scaler_path}. Train the pipeline first.")
        
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)
        
    scaled_nums = scaler.transform(df[num_cols])
    scaled_nums_df = pd.DataFrame(scaled_nums, columns=num_cols, index=df.index)
    
    # 4. Combine
    X = pd.concat([scaled_nums_df, encoded_cats_df], axis=1)
    
    return X, y
