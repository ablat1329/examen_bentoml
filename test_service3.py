import pytest
import httpx
import jwt
import datetime

BASE_URL = "http://127.0.0.1:3000"

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
    "GRE Score": "abc",  # invalid
    "TOEFL Score": None,
    "University Rating": "five"
}


@pytest.fixture
def get_valid_token():
    response = httpx.post(f"{BASE_URL}/login", json={"username": "admin", "password": "secret123"})
    assert response.status_code == 200
    return response.json()["token"]


def test_auth_fails_without_token():
    response = httpx.post(f"{BASE_URL}/predict", json=VALID_INPUT)
    assert response.status_code == 401
    assert "Unauthorized" in response.json().get("error", "")


def test_auth_fails_with_invalid_token():
    VALID_INPUT["token"] = "invalidtoken"
    response = httpx.post(f"{BASE_URL}/predict", json=VALID_INPUT)
    assert response.status_code == 401
    assert "Invalid token" in response.json().get("error", "")


def test_auth_fails_with_expired_token():
    expired_token = jwt.encode(
        {"username": "admin", "exp": datetime.datetime.utcnow() - datetime.timedelta(hours=1)},
        "supersecretkey", algorithm="HS256"
    )
    VALID_INPUT["token"] = expired_token
    response = httpx.post(f"{BASE_URL}/predict", json=VALID_INPUT)
    assert response.status_code == 401
    assert "Token expired" in response.json().get("error", "")


def test_login_succeeds_for_valid_credentials():
    response = httpx.post(f"{BASE_URL}/login", json={"username": "admin", "password": "secret123"})
    assert response.status_code == 200
    assert "token" in response.json()


def test_login_fails_for_invalid_credentials():
    response = httpx.post(f"{BASE_URL}/login", json={"username": "admin", "password": "wrongpass"})
    assert response.status_code == 401
    assert "Invalid username" in response.json().get("error", "")


def test_predict_returns_valid_prediction(get_valid_token):
    VALID_INPUT["token"] = get_valid_token
    response = httpx.post(f"{BASE_URL}/predict", json=VALID_INPUT)
    assert response.status_code == 200
    assert "prediction" in response.json()


def test_predict_returns_401_without_token():
    response = httpx.post(f"{BASE_URL}/predict", json=VALID_INPUT)
    assert response.status_code == 401
    assert "Unauthorized" in response.json().get("error", "")


def test_predict_fails_for_invalid_input(get_valid_token):
    INVALID_INPUT["token"] = get_valid_token
    response = httpx.post(f"{BASE_URL}/predict", json=INVALID_INPUT)
    assert response.status_code == 400
    assert "Invalid input" in response.json().get("error", "")
