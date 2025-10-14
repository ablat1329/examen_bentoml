import pytest
import httpx
import time
import jwt

BASE_URL = "http://127.0.0.1:3000"
SECRET_KEY = "supersecretkey"  # Must match your BentoML service secret key

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
    resp = httpx.post(f"{BASE_URL}/login", json=VALID_CREDENTIALS)
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data
    return data["token"]


@pytest.fixture
def get_expired_token():
    payload = {
        "username": "admin",
        "exp": time.time() - 10
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


# --------------------------
# Login API Tests
# --------------------------
def test_login_returns_token_for_valid_credentials():
    resp = httpx.post(f"{BASE_URL}/login", json=VALID_CREDENTIALS)
    assert resp.status_code == 200
    assert "token" in resp.json()


def test_login_fails_for_invalid_credentials():
    resp = httpx.post(f"{BASE_URL}/login", json=INVALID_CREDENTIALS)
    assert resp.status_code == 200
    assert "error" in resp.json()
    assert resp.json()["error"] == "Invalid username or password"


# --------------------------
# JWT Authentication Tests
# --------------------------
def test_auth_fails_without_token():
    resp = httpx.post(f"{BASE_URL}/predict", json=VALID_INPUT)
    assert resp.status_code == 200
    assert "error" in resp.json()
    assert "Token missing" in resp.json()["error"]


def test_auth_fails_with_invalid_token():
    payload = VALID_INPUT.copy()
    payload["token"] = "invalidtoken"
    resp = httpx.post(f"{BASE_URL}/predict", json=payload)
    assert resp.status_code == 200
    assert "error" in resp.json()
    assert "Invalid token" in resp.json()["error"]


def test_auth_fails_with_expired_token(get_expired_token):
    payload = VALID_INPUT.copy()
    payload["token"] = get_expired_token
    resp = httpx.post(f"{BASE_URL}/predict", json=payload)
    assert resp.status_code == 200
    assert "error" in resp.json()
    assert "Token expired" in resp.json()["error"]


def test_auth_succeeds_with_valid_token(get_valid_token):
    payload = VALID_INPUT.copy()
    payload["token"] = get_valid_token
    resp = httpx.post(f"{BASE_URL}/predict", json=payload)
    assert resp.status_code == 200
    assert "admission_chance" in resp.json()


# --------------------------
# Prediction API Tests
# --------------------------
def test_predict_returns_valid_prediction(get_valid_token):
    payload = VALID_INPUT.copy()
    payload["token"] = get_valid_token
    resp = httpx.post(f"{BASE_URL}/predict", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "admission_chance" in data
    assert isinstance(data["admission_chance"], float)


def test_predict_fails_for_invalid_input(get_valid_token):
    payload = INVALID_INPUT.copy()
    payload["token"] = get_valid_token
    resp = httpx.post(f"{BASE_URL}/predict", json=payload)
    assert resp.status_code == 200
    assert "error" in resp.json()
