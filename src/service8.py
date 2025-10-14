import bentoml
from bentoml.io import JSON
import pandas as pd
import jwt
import datetime

# Secret key for signing JWTs (in production: store securely, e.g. env variables)
SECRET_KEY = "supersecretkey"

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

# Load trained model
model_ref = bentoml.sklearn.get("admissions_model_with_scaler:latest")
model_runner = model_ref.to_runner()

# Create BentoML service
svc = bentoml.Service("admissions_service", runners=[model_runner])

VALID_USERS = {"admin": "secret123"}  # username: password


@svc.api(input=JSON(), output=JSON())
def login(credentials: dict):
    username = credentials.get("username")
    password = credentials.get("password")

    if username in VALID_USERS and VALID_USERS[username] == password:
        payload = {
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # token valid 1h
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return {"token": token}
    else:
        return {"error": "Invalid username or password"}


@svc.api(input=JSON.from_sample(example_input), output=JSON())
async def predict(input_data: dict):
    token = input_data.pop("token", None)

    if not token:
        return {"error": "Unauthorized. Token missing."}

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired. Please login again."}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token. Please login again."}

    try:
        df = pd.DataFrame([input_data])
        # Validate that all inputs are numeric
        if not all(df.dtypes.apply(lambda dt: pd.api.types.is_numeric_dtype(dt))):
            raise ValueError("All input features must be numeric.")

        prediction = await model_runner.predict.async_run(df)
        return {"admission_chance": float(prediction[0])}
    except Exception as e:
        return {"error": f"Invalid input data: {str(e)}"}
