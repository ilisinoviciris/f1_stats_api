# ML for predicting race pace evolution
# uses Random Forest as baseline

from ml import utils
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def load_data(csv_path: str = "laps_dataset.csv") -> pd.DataFrame:
    """Load the dataset."""
    return pd.read_csv(csv_path)

# prepare data for training
def prepare_data(df: pd.DataFrame):
    """
    Seperate numerical and categorical attributes.
    Define predictors and target.
    """
    num_attribs = ["lap_number", "stint_number", "stint_lap_number"]
    cat_attribs = ["tyre_compound", "team_name", "circuit_name"]
    target = ["lap_duration"]

    X = df[num_attribs + cat_attribs]
    y = df[target]
    
    return X, y, num_attribs, cat_attribs

# create ML pipeline
def build_pipeline(num_attribs, cat_attribs) -> Pipeline:
    """
    Sub-pipelines for numerical and categorical data.
    Column transformer to implement the above named sub-pipelines.
    Final pipeline that implements column transfomer and selects Linear regression model.
    """
    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("std_scaler", StandardScaler())
    ])

    cat_pipeline = Pipeline([
        ("ohe", OneHotEncoder())
    ])


    full_pipeline = ColumnTransformer([
        ("num", num_pipeline, num_attribs),
        ("cat", cat_pipeline, cat_attribs)
    ])

    model = Pipeline([
        ("preprocessor", full_pipeline),
        ("regressor", RandomForestRegressor(
            n_estimators=100,
            max_depth=None,
            random_state=42,
            n_jobs=-1
        ))
    ])

    return model

# train and evaluate model
def train_and_evaluate(model, X, y, test_size=0.3, random_state=42):
    """Train/test split, training and evaluating the model."""
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    model.fit(X_train, y_train.values.ravel())

    y_pred = model.predict(X_test)
    
    metrics = {
        "r2": float(r2_score(y_test, y_pred)),
        "mae": float(mean_absolute_error(y_test, y_pred)),
        "mse": float(mean_squared_error(y_test, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred)))
    }

    train_r2 = model.score(X_train, y_train)
    test_r2 = model.score(X_test, y_test)

    print("Evaluation metrics:", metrics)
    print(f"Train R2: {train_r2:.4f}")
    print(f"Test R2: {test_r2:.4f}")

    return model, X_test, y_test, y_pred, metrics

def main():
    df = load_data()
    df = df[df["session_name"] == "Race"]

    X, y, num_attribs, cat_attribs = prepare_data(df)

    model = build_pipeline(num_attribs, cat_attribs)
    model, X_test, y_test, y_pred, metrics = train_and_evaluate(model, X, y)

    model_name = "race_pace_random_forest"
    utils.save_model(model, model_name)
    utils.save_metrics(metrics, model_name)

    utils.plot_feature_importance(model, X, model_name="race_pace_random_forest")

if __name__ == "__main__":
    main()