# util functions for dataset and saving artifacts

import joblib
import json
from pathlib import Path
import matplotlib.pyplot as plt

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
