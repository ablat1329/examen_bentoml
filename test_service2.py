import pytest
import httpx
import jwt
import datetime

BASE_URL = "http://localhost:3000"  # BentoML default serve port

SECRET_KEY = "supersecretkey"

VALID_CREDENTIALS = {"username": "admin", "password": "secret123"}
INVALID_CREDENTIALS = {"username": "admin", "password": "wrongpass"}

VALID_INPUT = {
    "GRE Score": 320,
    "TOEFL Score": 110,
    "University Rating": 4,
    "SOP": 4.5,
    "LOR": 4.5,
    "CGPA": 9.0,
    "Research": 1,
    "token": ""
}

INVALID_INPUT = {
    "GRE Score": "invalid",  # wrong type
    "TOEFL Score": None,
    "University Rating": "none"
}


@pytest.fixture
def get_valid_token():
    payload = {
        "username": "admin",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def test_auth_fails_without_token():
    response = httpx.post(f"{BASE_URL}/predict", json=VALID_INPUT)
    assert response.status_code == 401


def test_auth_fails_with_invalid_token():
    VALID_INPUT["token"] = "invalidtoken"
    response = httpx.post(f"{BASE_URL}/predict", json=VALID_INPUT)
    assert response.status_code == 401


def test_auth_fails_with_expired_token():
    payload = {
        "username": "admin",
        "exp": datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    }
    expired_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    VALID_INPUT["token"] = expired_token
    response = httpx.post(f"{BASE_URL}/predict", json=VALID_INPUT)
    assert response.status_code == 401


def test_login_returns_valid_token():
    response = httpx.post(f"{BASE_URL}/login", json=VALID_CREDENTIALS)
    assert response.status_code == 200
    assert "token" in response.json()


def test_login_fails_for_invalid_credentials():
    response = httpx.post(f"{BASE_URL}/login", json=INVALID_CREDENTIALS)
    assert response.status_code == 401


def test_predict_returns_valid_prediction(get_valid_token):
    VALID_INPUT["token"] = get_valid_token
    response = httpx.post(f"{BASE_URL}/predict", json=VALID_INPUT)
    assert response.status_code == 200
    assert "prediction" in response.json()


def test_predict_returns_401_without_token():
    response = httpx.post(f"{BASE_URL}/predict", json=VALID_INPUT)
    assert response.status_code == 401


def test_predict_fails_for_invalid_input(get_valid_token):
    INVALID_INPUT["token"] = get_valid_token
    response = httpx.post(f"{BASE_URL}/predict", json=INVALID_INPUT)
    assert response.status_code == 400
