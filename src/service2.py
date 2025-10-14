# src/service.py

import bentoml
from bentoml.io import JSON
import pandas as pd

# Load the latest saved model
model_ref = bentoml.sklearn.get("admissions_model_with_scaler:latest")
model_runner = model_ref.to_runner()

# Define the BentoML service
svc = bentoml.Service("admissions_service", runners=[model_runner])

# API endpoint
@svc.api(input=JSON(), output=JSON())
def predict(input_data):
    """
    Expects JSON input with feature names and values.
    Example:
    {
      "GRE Score": 320,
      "TOEFL Score": 110,
      "University Rating": 4,
      "SOP": 4.5,
      "LOR": 4.5,
      "CGPA": 9.0,
      "Research": 1
    }
    """
    # Convert dict to DataFrame (1 row)
    df = pd.DataFrame([input_data])
    prediction = model_runner.predict.run(df)
    return {"admission_chance": float(prediction[0])}


# Allow running with `python src/service.py`
if __name__ == "__main__":
    # This will start a local HTTP server at http://127.0.0.1:3000
    svc.run()


# bentoml serve src.service2:svc
# bentoml serve src/service2.py:svc
# python src/service2.py # do NOT work, in the new version of BentoML > 1.XX,
# python src/service2.py # do     work, in the old version of BentoML 0.13.x/0.14.x

