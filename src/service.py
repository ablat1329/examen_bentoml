# src/service.py

import bentoml
from bentoml.io import JSON

model_runner = bentoml.sklearn.get("admissions_model_with_scaler:latest").to_runner()

svc = bentoml.Service("admissions_service", runners=[model_runner])

@svc.api(input=JSON(), output=JSON())
def predict(input_data):
    return model_runner.predict.run(input_data)

