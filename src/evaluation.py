import os
import json
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_recall_fscore_support
from src.utils import load_config

def evaluate_model(X_test, y_test, config_path="config/config.yaml"):
    """
    Evaluates the model on test set, prints metrics, saves metrics JSON and confusion matrix plot.
    """
    config = load_config(config_path)
    
    model_path = config["model"]["model_path"]
    cm_path = config["reports"]["confusion_matrix_path"]
    metrics_path = config["reports"]["metrics_path"]
    
    print(f"[Evaluation] Loading model from {model_path}...")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}. Train the model first.")
        
    with open(model_path, "rb") as f:
        model = pickle.load(f)
        
    print("[Evaluation] Generating predictions on the test set...")
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary')
    
    print("\n" + "=" * 50)
    print("                 EVALUATION RESULTS")
    print("=" * 50)
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    print("=" * 50)
    
    print("\nClassification Report:")
    report_dict = classification_report(y_test, y_pred, output_dict=True)
    report_str = classification_report(y_test, y_pred)
    print(report_str)
    
    # Save metrics JSON
    metrics = {
        "accuracy": accuracy,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "classification_report": report_dict
    }
    
    os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4)
    print(f"[Evaluation] Saved metrics summary to {metrics_path}")
    
    # Generate Confusion Matrix Plot
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    
    # Map target numeric labels back to categories for plotting
    target_map = config["features"]["target_mapping"]
    labels = sorted(target_map, key=target_map.get)  # e.g., ['neutral or dissatisfied', 'satisfied']
    
    sns.heatmap(
        cm, 
        annot=True, 
        fmt="d", 
        cmap="Blues", 
        xticklabels=labels, 
        yticklabels=labels,
        annot_kws={"size": 14}
    )
    plt.title("Confusion Matrix: Airline Passenger Satisfaction", fontsize=16, pad=15)
    plt.ylabel("Actual Label", fontsize=12)
    plt.xlabel("Predicted Label", fontsize=12)
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(cm_path), exist_ok=True)
    plt.savefig(cm_path, dpi=300)
    plt.close()
    print(f"[Evaluation] Saved confusion matrix plot to {cm_path}")
    
    return metrics

if __name__ == "__main__":
    pass
