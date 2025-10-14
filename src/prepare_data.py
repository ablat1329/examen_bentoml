# src/prepare_data.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os
import joblib

# Paths
RAW_DATA_PATH = "data/raw/admission.csv"
PROCESSED_DATA_DIR = "data/processed"

os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

def load_and_clean_data(path):
    df = pd.read_csv(path)

    # Drop irrelevant columns (example: Serial No)
    drop_cols = ['Serial No.'] if 'Serial No.' in df.columns else []
    df.drop(columns=drop_cols, inplace=True)

    df.dropna(inplace=True)  # Remove missing values
    return df

def split_and_scale(df):
    y = df["Chance of Admit "].copy()
    X = df.drop(columns=["Chance of Admit "])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Feature scaling
    scaler = StandardScaler()
    X_train_scaled_array = scaler.fit_transform(X_train)
    X_test_scaled_array = scaler.transform(X_test)

    # Convert back to DataFrame to preserve column names
    X_train_scaled = pd.DataFrame(X_train_scaled_array, columns=X_train.columns)
    X_test_scaled = pd.DataFrame(X_test_scaled_array, columns=X_test.columns)


    # Save scaler for later use
    joblib.dump(scaler, os.path.join(PROCESSED_DATA_DIR, "scaler.joblib"))

    return X_train_scaled, X_test_scaled, y_train, y_test

def save_data(X_train, X_test, y_train, y_test):
    pd.DataFrame(X_train).to_csv(os.path.join(PROCESSED_DATA_DIR, "X_train.csv"), index=False)
    pd.DataFrame(X_test).to_csv(os.path.join(PROCESSED_DATA_DIR, "X_test.csv"), index=False)
    y_train.to_csv(os.path.join(PROCESSED_DATA_DIR, "y_train.csv"), index=False)
    y_test.to_csv(os.path.join(PROCESSED_DATA_DIR, "y_test.csv"), index=False)

if __name__ == "__main__":
    df = load_and_clean_data(RAW_DATA_PATH)
    X_train, X_test, y_train, y_test = split_and_scale(df)
    save_data(X_train, X_test, y_train, y_test)
    print("Data preparation with scaling completed.")

