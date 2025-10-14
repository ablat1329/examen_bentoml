# src/train_model.py

import pandas as pd
import bentoml
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.model_selection import GridSearchCV
import os
import joblib
import numpy as np

PROCESSED_DATA_DIR = "data/processed"

def load_data():
    X_train = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "X_train.csv"))
    X_test = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "X_test.csv"))
    y_train = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "y_train.csv"))
    y_test = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "y_test.csv"))

    return X_train.values, X_test.values, y_train.values.ravel(), y_test.values.ravel()

def train_with_gridsearch(X_train, y_train):
    model = RandomForestRegressor(random_state=42)

    param_grid = {
        "n_estimators": [50, 100, 200],
        "max_depth": [None, 10, 20],
        "min_samples_split": [2, 5, 10],
        "min_samples_leaf": [1, 2, 4]
    }

    grid_search = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        cv=3,
        n_jobs=-1,
        verbose=1,
        scoring="r2"
    )

    grid_search.fit(X_train, y_train)
    print(f"Best parameters: {grid_search.best_params_}")
    return grid_search.best_estimator_

def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)
    r2 = r2_score(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    print(f"Model Performance:\nR² Score: {r2:.4f}\nRMSE: {rmse:.4f}")
    return r2, rmse

def save_model(model):
    bentoml.sklearn.save_model("admissions_model_direct", model)
    print("Model saved to BentoML Model Store.")

def save_model_with_scaler(model, scaler):
    class AdmissionsModel(bentoml.Runnable):
        SUPPORTED_RESOURCES = ("cpu",)
        SUPPORTED_BATCH_MODE = False

        def __init__(self):
            self.model = model
            self.scaler = scaler

        @bentoml.Runnable.method(batchable=False)
        def predict(self, X):
            X_scaled = self.scaler.transform(X)
            return self.model.predict(X_scaled)

    bentoml.sklearn.save_model(
        "admissions_model_with_scaler",
        model,
        custom_objects={"scaler": scaler}
    )
    print("Model with scaler saved to BentoML Model Store.")

if __name__ == "__main__":
    X_train, X_test, y_train, y_test = load_data()
    model = train_with_gridsearch(X_train, y_train)
    evaluate_model(model, X_test, y_test)
    save_model(model)

    # load scaler
    myscaler = joblib.load(os.path.join(PROCESSED_DATA_DIR, "scaler.joblib"))
    # save model with scaler
    save_model_with_scaler(model, myscaler)

