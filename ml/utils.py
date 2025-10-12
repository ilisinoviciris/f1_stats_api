# util functions for dataset and saving artifacts

import joblib
import json
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# default path
ML_DIR = Path("ml")

def save_model(model, model_name: str):
    """Save model in ml/models/{model_name}/model.pkl."""
    model_dir = ML_DIR / "models" / model_name
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "model.pkl"

    joblib.dump(model, model_path)

    return model_path
    
def save_metrics(metrics: dict, model_name: str):
    """Save metrics in ml/metrics/{model_name}/metrics.json."""
    metrics_dir = ML_DIR / "metrics" / model_name
    metrics_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = metrics_dir / "metrics.json"

    with open(metrics_path, "w", encoding="utf-8") as m:
        json.dump(metrics, m, indent=2)

    return metrics_path

def save_plot(fig: plt.Figure, model_name: str, filename: str = "plot.png"):
    """Save plot in ml/plots/{model_name}/{filename}"""
    plot_dir = ML_DIR / "plots" / model_name
    plot_dir.mkdir(parents=True, exist_ok=True)
    plot_path = plot_dir / filename
    fig.savefig(plot_path)
    plt.close(fig)

    return plot_path

def load_model(model_name: str):
    """Load saved .pkl model."""
    model_path = ML_DIR / "models" / model_name / "model.pkl"
    model = joblib.load(model_path)
    
    return model

def plot_feature_importance(model, X, model_name: str, filename="feature_importance_plot.png"):
    """Generate and save plot for top 10 feature importances for Random Forest model."""
    regressor = model.named_steps["regressor"]
    preprocessor = model.named_steps["preprocessor"]

    cat_features = preprocessor.named_transformers_["cat"]["ohe"].get_feature_names_out(preprocessor.transformers_[1][2])
    num_features = preprocessor.transformers_[0][2]
    all_features = np.concatenate([num_features, cat_features])

    importances = regressor.feature_importances_
    indices = np.argsort(importances)[::-1][:10]
    top_features = all_features[indices]
    top_importances = importances[indices]

    plot_dir = ML_DIR / "plots" / model_name
    plot_dir.mkdir(parents=True, exist_ok=True)
    plot_path = plot_dir / filename

    fig, ax = plt.subplots(figsize=(14,8))

    bars = ax.bar(range(len(top_features)), top_importances, color="#32a4a8", edgecolor="black", linewidth=1)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height, f"{height:.4f}", ha="center", va="bottom", fontsize=8)

    ax.set_title(f"Top 10 Feature Importances", fontsize=18, loc="center", y=1.04, weight="bold")
    ax.set_xlabel("Features")
    ax.set_ylabel("Importance")
    ax.set_xticks(range(len(top_features)))
    ax.set_xticklabels(top_features, rotation=45, ha="center", fontsize=10, wrap=True)
    
    fig.savefig(plot_path)
    plt.close(fig)

    return plot_path