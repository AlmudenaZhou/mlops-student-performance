import os
import sys
sys.path.append(os.getcwd())

from flask import Flask, request, jsonify

from scripts import load_models, predict


TEST_RUN = os.getenv("TEST_RUN", "False") == "True"

if TEST_RUN:
    MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", None)
    print(MLFLOW_TRACKING_URI)

    from dotenv import load_dotenv
    load_dotenv()

    if MLFLOW_TRACKING_URI is not None: 
        os.environ["MLFLOW_TRACKING_URI"] = MLFLOW_TRACKING_URI

RUN_ID = os.getenv("RUN_ID")
EXPERIMENT_NAME = os.getenv("EXPERIMENT_NAME")
model, scaler = load_models()

print("model and scaler downloaded")
app = Flask(EXPERIMENT_NAME)


@app.route('/predict', methods=['POST'])
def predict_endpoint():
    student = request.get_json()

    pred = predict(model, scaler, student)

    result = {
        'GPA': pred,
        'model_version': RUN_ID
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=9696)
