import pytest
import bentoml
from bentoml.testing import TestClient
import time
import jwt
import datetime

from your_service_file import svc, SECRET_KEY  # Replace with your actual service filename


# ---------------------
# Setup
# ---------------------
client = TestClient(svc)

VALID_CREDENTIALS = {"username": "admin", "password": "secret123"}
INVALID_CREDENTIALS = {"username": "admin", "password": "wrongpass"}

EXAMPLE_INPUT = {
    "GRE Score": 320,
    "TOEFL Score": 110,
    "University Rating": 4,
    "SOP": 4.5,
    "LOR": 4.5,
    "CGPA": 9.0,
    "Research": 1
}


# ---------------------
# Login API Tests
# ---------------------
def test_login_success():
    response = client.post("/login", json=VALID_CREDENTIALS)
    assert response.status_code == 200
    data = response.json()
    assert "token" in data

def test_login_failure():
    response = client.post("/login", json=INVALID_CREDENTIALS)
    assert response.status_code == 200
    data = response.json()
    assert "error" in data and data["error"] == "Invalid username or password"


# ---------------------
# JWT Authentication Tests
# ---------------------
def test_missing_token():
    payload = EXAMPLE_INPUT.copy()
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "error" in data and "Token missing" in data["error"]

def test_invalid_token():
    payload = EXAMPLE_INPUT.copy()
    payload["token"] = "invalidtoken"
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "error" in data and "Invalid token" in data["error"]

def test_expired_token():
    expired_payload = {
        "username": "admin",
        "exp": datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
    }
    expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm="HS256")

    payload = EXAMPLE_INPUT.copy()
    payload["token"] = expired_token

    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "error" in data and "Token expired" in data["error"]

def test_valid_token_auth():
    login_resp = client.post("/login", json=VALID_CREDENTIALS)
    token = login_resp.json().get("token")

    payload = EXAMPLE_INPUT.copy()
    payload["token"] = token

    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "admission_chance" in data


# ---------------------
# Prediction API Tests
# ---------------------
def test_prediction_with_valid_data():
    login_resp = client.post("/login", json=VALID_CREDENTIALS)
    token = login_resp.json().get("token")

    payload = EXAMPLE_INPUT.copy()
    payload["token"] = token

    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("admission_chance"), float)

def test_prediction_with_invalid_data():
    login_resp = client.post("/login", json=VALID_CREDENTIALS)
    token = login_resp.json().get("token")

    payload = {"GRE Score": "invalid", "token": token}
    response = client.post("/predict", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "error" in data or "admission_chance" not in data
