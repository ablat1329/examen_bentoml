import pytest
import httpx
import time
import jwt

BASE_URL = "http://127.0.0.1:3000"  # Change if different
SECRET_KEY = "your_jwt_secret"  # Must match your Bento service JWT secret

VALID_CREDENTIALS = {"username": "admin", "password": "secret123"}
INVALID_CREDENTIALS = {"username": "wrong", "password": "wrong"}

VALID_INPUT = {
    "GRE Score": 320,
    "TOEFL Score": 110,
    "University Rating": 4,
    "SOP": 4.5,
    "LOR": 4.5,
    "CGPA": 9.0,
    "Research": 1
}

INVALID_INPUT = {
    "GRE Score": "invalid",  # Should be numeric
    "TOEFL Score": None
}


@pytest.fixture
def get_valid_token():
    # Login to get a valid JWT token
    response = httpx.post(f"{BASE_URL}/login", json=VALID_CREDENTIALS)
    assert response.status_code == 200
    return response.json()["token"]


@pytest.fixture
def get_expired_token():
    # Create an expired token manually
    payload = {"user": "admin", "exp": time.time() - 10}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


# --------------------------
# JWT Authentication Tests
# --------------------------
def test_auth_fails_without_token():
    response = httpx.post(f"{BASE_URL}/predict", json=VALID_INPUT)
    assert response.status_code == 401


def test_auth_fails_with_invalid_token():
    headers = {"Authorization": "Bearer invalidtoken"}
    response = httpx.post(f"{BASE_URL}/predict", json=VALID_INPUT, headers=headers)
    assert response.status_code == 401


def test_auth_fails_with_expired_token(get_expired_token):
    headers = {"Authorization": f"Bearer {get_expired_token}"}
    response = httpx.post(f"{BASE_URL}/predict", json=VALID_INPUT, headers=headers)
    assert response.status_code == 401


def test_auth_succeeds_with_valid_token(get_valid_token):
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = httpx.post(f"{BASE_URL}/predict", json=VALID_INPUT, headers=headers)
    assert response.status_code != 401


# --------------------------
# Login API Tests
# --------------------------
def test_login_returns_token_for_valid_credentials():
    response = httpx.post(f"{BASE_URL}/login", json=VALID_CREDENTIALS)
    assert response.status_code == 200
    assert "token" in response.json()


def test_login_fails_for_invalid_credentials():
    response = httpx.post(f"{BASE_URL}/login", json=INVALID_CREDENTIALS)
    assert response.status_code == 401


# --------------------------
# Prediction API Tests
# --------------------------
def test_predict_returns_401_without_token():
    response = httpx.post(f"{BASE_URL}/predict", json=VALID_INPUT)
    assert response.status_code == 401


def test_predict_returns_valid_prediction(get_valid_token):
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = httpx.post(f"{BASE_URL}/predict", json=VALID_INPUT, headers=headers)
    assert response.status_code == 200
    assert "prediction" in response.json()


def test_predict_fails_for_invalid_input(get_valid_token):
    headers = {"Authorization": f"Bearer {get_valid_token}"}
    response = httpx.post(f"{BASE_URL}/predict", json=INVALID_INPUT, headers=headers)
    assert response.status_code == 400

