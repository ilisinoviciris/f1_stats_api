# ML for predicting race pace evolution
# uses LinearRegression as baseline

from ml import utils
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
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
    cat_attribs = ["race_id", "driver_id", "tyre_compound"]
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
        ("regressor", LinearRegression())
    ])

    return model

# train and evaluate model
def train_and_evaluate(model, X, y, test_size=0.3, random_state=42):
    """Train/test split, training and evaluating the model."""
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    
    metrics = {
        "r2": float(r2_score(y_test, y_pred)),
        "mae": float(mean_absolute_error(y_test, y_pred)),
        "mse": float(mean_squared_error(y_test, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred)))
    }

    print("Evaluation metrics:", metrics)

    return model, X_test, y_test, y_pred, metrics

# print coefficients for all features
def print_coefficients(model, num_attribs, cat_attribs):
    """
    Prints linear regression coefficients for all features.
    """
    lin_reg = model.named_steps["regressor"]
    preprocessor = model.named_steps["preprocessor"]

    # get names of categorical features after OneHotEncoder
    cat_features = preprocessor.named_transformers_["cat"]["ohe"].get_feature_names_out(cat_attribs)
    all_features = np.concatenate([num_attribs, cat_features])

    coefficients = lin_reg.coef_
    intercept = lin_reg.intercept_

    print("Model coefficients (Linear Regression):\n")
    print(f"Intercept: {intercept}")
    for name, coef in zip(all_features, coefficients):
        print(f"{name}:{coef}")

# visualizing predictions with matplotlib
def plot_scatter_predictions(y_test, y_pred):
    """Scatter plot: prediction vs actual results."""
    fig, ax = plt.subplots(figsize=(8,6))
    ax.scatter(y_test, y_pred, alpha=0.5, color="blue", edgecolors="k")
    ax.plot([y_test.min(),y_test.max()], [y_test.min(), y_test.max()], color="red", lw=1.5)

    ax.set_xlabel("Actual Lap Time")
    ax.set_ylabel("Predicted Lap Duration")
    ax.set_title("Linear regression: Predicted vs Actual Lap Times")
    
    return fig

def main():
    df = load_data()
    df = df[df["session_name"] == "Race"]

    X, y, num_attribs, cat_attribs = prepare_data(df)

    model = build_pipeline(num_attribs, cat_attribs)
    model, X_test, y_test, y_pred, metrics = train_and_evaluate(model, X, y)

    print_coefficients(model, num_attribs, cat_attribs)

    model_name = "race_pace_linear"
    utils.save_model(model, model_name)
    utils.save_metrics(metrics, model_name)

    fig = plot_scatter_predictions(y_test, y_pred)
    utils.save_plot(fig, model_name, "scatter_plot.png")

if __name__ == "__main__":
    main()