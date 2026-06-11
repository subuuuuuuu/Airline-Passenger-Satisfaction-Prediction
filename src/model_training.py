import os
import pickle
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from src.utils import load_config

def train_model(X_train, y_train, config_path="config/config.yaml"):
    """
    Initializes a RandomForestClassifier, performs hyperparameter tuning
    using GridSearchCV based on config settings, and saves the best model.
    """
    config = load_config(config_path)
    
    model_path = config["model"]["model_path"]
    random_state = config["model"]["random_state"]
    gs_config = config["model"]["grid_search"]
    
    param_grid = gs_config["param_grid"]
    cv = gs_config["cv"]
    scoring = gs_config["scoring"]
    n_jobs = gs_config["n_jobs"]
    
    print("[Training] Initializing RandomForestClassifier...")
    rf = RandomForestClassifier(random_state=random_state)
    
    print(f"[Training] Running GridSearchCV with parameter grid:")
    for key, val in param_grid.items():
        print(f"  - {key}: {val}")
    print(f"[Training] Folds: {cv} | Metric: {scoring}")
    
    # Run Grid Search
    grid_search = GridSearchCV(
        estimator=rf,
        param_grid=param_grid,
        cv=cv,
        scoring=scoring,
        n_jobs=n_jobs,
        verbose=1
    )
    
    print("[Training] Fitting GridSearchCV...")
    grid_search.fit(X_train, y_train)
    
    best_params = grid_search.best_params_
    best_score = grid_search.best_score_
    print(f"[Training] GridSearchCV completed!")
    print(f"[Training] Best validation score ({scoring}): {best_score:.4f}")
    print(f"[Training] Best parameters: {best_params}")
    
    best_model = grid_search.best_estimator_
    
    # Save the model
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, "wb") as f:
        pickle.dump(best_model, f)
    print(f"[Training] Saved best model to {model_path}")
    
    return best_model

if __name__ == "__main__":
    # Test stub
    pass
