import os

from flask import Flask, request, jsonify
from dotenv import load_dotenv


import sys
cwd = os.getcwd()
sys.path.append(cwd) 
print(sys.path)

from scripts import load_models, predict


load_dotenv()

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
