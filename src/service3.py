import bentoml
import pandas as pd
from bentoml.io import JSON

# Load your trained model
model_ref = bentoml.sklearn.get("admissions_model_with_scaler:latest")
model_runner = model_ref.to_runner()

# Define the service with runners
svc = bentoml.Service("admissions_service", runners=[model_runner])

# Example input
example_input = {
    "GRE Score": 320,
    "TOEFL Score": 110,
    "University Rating": 4,
    "SOP": 4.5,
    "LOR": 4.5,
    "CGPA": 9.0,
    "Research": 1
}

@svc.api(input=JSON.from_sample(example_input), output=JSON())
async def predict(input_data: dict):
    df = pd.DataFrame([input_data])
    prediction = await model_runner.predict.async_run(df)
    return {"admission_chance": float(prediction[0])}

if __name__ == "__main__":
    svc.run()


# BentoML 0.x (legacy)
# Services defined with decorators like @bentoml.artifacts, @bentoml.api
# Could use svc.run()

# BentoML 1.0.x (what you’re using)
# You must define services with bentoml.Service objects


# BentoML 1.1+ (newer, released later), install 1.4.22
# Introduced @bentoml.service decorator (syntactic sugar)


