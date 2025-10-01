# util functions for dataset and saving artifacts

import joblib
import json
from pathlib import Path

# default paths
ML_DIR = Path("ml")
MODELS_DIR = ML_DIR / "models"
METRICS_DIR = ML_DIR / "metrics"
PLOTS_DIR = ML_DIR / "plots"

for d in [MODELS_DIR, METRICS_DIR, PLOTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def save_model(model, model_name: str):
    """Save model in ml/models/<model_name>/model.pkl."""
    model_dir = MODELS_DIR / model_name
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "model.pkl"

    joblib.dump(model, model_path)

    return model_path
    
def save_metrics(metrics: dict, model_name: str):
    """Save metrics in ml/metrics/<model_name>/metrics.json."""
    metrics_dir = METRICS_DIR / model_name
    metrics_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = metrics_dir / "metrics.json"

    with open(metrics_path, "w", encoding="utf-8") as m:
        json.dump(metrics, m, indent=2)

    return metrics_path

def create_plot_dir(model_name: str):
    """Create directory for saving plots in ml/plots/<model_name>/ and return path."""
    plot_dir = PLOTS_DIR / model_name
    plot_dir.mkdir(parents=True, exist_ok=True)

    return plot_dir

def load_model(model_name: str):
    """Load saved .pkl model."""
    model_path = MODELS_DIR / model_name / "model.pkl"
    model = joblib.load(model_path)
    
    return model
