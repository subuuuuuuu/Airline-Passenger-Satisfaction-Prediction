import os
import pickle
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.impute import SimpleImputer
from src.utils import load_config

def preprocess_data(df, config_path="config/config.yaml", is_train=True):
    """
    Performs data cleaning: dropping index columns, imputing missing values, and outlier removal.
    Fitted imputer is saved to models/ during training and loaded during testing.
    """
    config = load_config(config_path)
    df = df.copy()
    
    # 1. Drop unnecessary columns
    drop_cols = config["preprocessing"].get("drop_columns", [])
    cols_to_drop = [c for c in drop_cols if c in df.columns]
    
    # Also drop pandas default 'Unnamed: 0' if it gets loaded
    unnamed_cols = [c for c in df.columns if c.startswith("Unnamed:")]
    cols_to_drop.extend(unnamed_cols)
    
    if cols_to_drop:
        cols_to_drop = list(set(cols_to_drop))
        print(f"[Preprocessing] Dropping columns: {cols_to_drop}")
        df = df.drop(columns=cols_to_drop)
        
    # 2. Impute missing values
    impute_config = config["preprocessing"]["imputation"]
    impute_cols = impute_config["columns"]
    strategy = impute_config["strategy"]
    imputer_path = "models/imputer.pkl"
    
    # Filter columns that are actually present
    impute_cols_present = [c for c in impute_cols if c in df.columns]
    
    if impute_cols_present:
        if is_train:
            print(f"[Preprocessing] Fitting SimpleImputer (strategy='{strategy}') on columns: {impute_cols_present}")
            imputer = SimpleImputer(strategy=strategy)
            df[impute_cols_present] = imputer.fit_transform(df[impute_cols_present])
            
            # Save the imputer
            os.makedirs(os.path.dirname(imputer_path), exist_ok=True)
            with open(imputer_path, "wb") as f:
                pickle.dump(imputer, f)
            print(f"[Preprocessing] Saved fitted imputer to {imputer_path}")
        else:
            print(f"[Preprocessing] Loading fitted imputer from {imputer_path}")
            if not os.path.exists(imputer_path):
                raise FileNotFoundError(f"Fitted imputer not found at {imputer_path}. Train the pipeline first.")
            with open(imputer_path, "rb") as f:
                imputer = pickle.load(f)
            df[impute_cols_present] = imputer.transform(df[impute_cols_present])
            
    # 3. Outlier removal (TRAIN ONLY)
    if is_train:
        outlier_config = config["preprocessing"]["outliers"]
        method = outlier_config["method"]
        initial_rows = df.shape[0]
        
        if method == "hardcoded":
            thresholds = outlier_config["hardcoded_thresholds"]
            print(f"[Preprocessing] Removing outliers using hardcoded thresholds: {thresholds}")
            
            # Apply thresholds if columns exist
            mask = pd.Series(True, index=df.index)
            for col, limit in thresholds.items():
                if col in df.columns:
                    mask = mask & (df[col] < limit)
            df = df[mask]
            
        elif method == "zscore":
            z_threshold = outlier_config["zscore_threshold"]
            print(f"[Preprocessing] Removing outliers using Z-score threshold: {z_threshold}")
            
            # Select numerical columns for outlier detection
            num_cols = config["features"]["numerical_columns"]
            num_cols_present = [c for c in num_cols if c in df.columns]
            
            if num_cols_present:
                z_scores = np.abs(stats.zscore(df[num_cols_present].select_dtypes(include=[np.number])))
                mask = (z_scores < z_threshold).all(axis=1)
                df = df[mask]
                
        else:
            print("[Preprocessing] Skipping outlier removal (method set to none/unknown)")
            
        rows_removed = initial_rows - df.shape[0]
        if rows_removed > 0:
            pct_removed = (rows_removed / initial_rows) * 100
            print(f"[Preprocessing] Removed {rows_removed} outliers ({pct_removed:.2f}% of data)")
            
    return df

if __name__ == "__main__":
    # Test on raw data
    config = load_config()
    df = pd.read_csv(config["data"]["raw_path"])
    df_clean = preprocess_data(df, is_train=True)
    print(f"Preprocessed train shape: {df_clean.shape}")
