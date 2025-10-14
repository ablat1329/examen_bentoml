import bentoml
from bentoml.io import JSON
import pandas as pd

# Example schema for Swagger
example_input = {
    "GRE Score": 320,
    "TOEFL Score": 110,
    "University Rating": 4,
    "SOP": 4.5,
    "LOR": 4.5,
    "CGPA": 9.0,
    "Research": 1
}

# Load the trained model
model_ref = bentoml.sklearn.get("admissions_model_with_scaler:latest")
model_runner = model_ref.to_runner()

# Create the service
svc = bentoml.Service("admissions_service", runners=[model_runner])

# Simple in-memory authentication store
VALID_USERS = {"admin": "secret123"}  # username: password
TOKENS = set()  # store active tokens (in real case: JWT, OAuth2 etc.)


@svc.api(input=JSON(), output=JSON())
def login(credentials: dict):
    """
    Simple login endpoint.
    Expects: {"username": "...", "password": "..."}
    Returns: {"token": "..."}
    """
    username = credentials.get("username")
    password = credentials.get("password")

    if username in VALID_USERS and VALID_USERS[username] == password:
        token = f"token-{username}"
        TOKENS.add(token)
        return {"token": token}
    else:
        return {"error": "Invalid username or password"}


@svc.api(input=JSON.from_sample(example_input), output=JSON())
async def predict(input_data: dict):
    """
    Prediction endpoint.
    Requires a valid token in the input payload: {"token": "...", features...}
    """
    print("TOKENS at start:", TOKENS) # debug output
    token = input_data.pop("token", None)

    if token not in TOKENS:
        return {"error": "Unauthorized. Please login first."}

    # Convert input features to DataFrame
    df = pd.DataFrame([input_data])
    prediction = await model_runner.predict.async_run(df)
    return {"admission_chance": float(prediction[0])}

# this works, Bentoml version 1.0.21
