import os
import pandas as pd
from sklearn.model_selection import train_test_split
from src.utils import load_config

def ingest_data(config_path="config/config.yaml"):
    """
    Loads raw data, splits it into train/test, and saves to processed folder.
    """
    config = load_config(config_path)
    
    raw_path = config["data"]["raw_path"]
    train_path = config["data"]["train_path"]
    test_path = config["data"]["test_path"]
    test_size = config["data"]["test_size"]
    random_state = config["data"]["random_state"]
    target_col = config["features"]["target_column"]
    
    print(f"[Ingestion] Loading raw dataset from: {raw_path}")
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw data file not found at: {raw_path}")
        
    df = pd.read_csv(raw_path)
    print(f"[Ingestion] Loaded dataset shape: {df.shape}")
    
    # Stratified train-test split based on satisfaction
    print(f"[Ingestion] Splitting dataset into train ({100*(1-test_size):.0f}%) and test ({100*test_size:.0f}%) subsets...")
    
    # Handle possible NaN in satisfaction for splitting
    if df[target_col].isnull().any():
        print("[Ingestion] Warning: Target column contains nulls. Removing null target rows before splitting.")
        df = df.dropna(subset=[target_col])
        
    train_df, test_df = train_test_split(
        df,
        test_size=test_size,
        stratify=df[target_col],
        random_state=random_state
    )
    
    # Ensure processed directory exists
    os.makedirs(os.path.dirname(train_path), exist_ok=True)
    
    # Save the splits
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    
    print(f"[Ingestion] Saved train set to: {train_path} | Shape: {train_df.shape}")
    print(f"[Ingestion] Saved test set to: {test_path} | Shape: {test_df.shape}")
    
    return train_path, test_path

if __name__ == "__main__":
    ingest_data()
