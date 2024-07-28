import sys
from pathlib import Path

import numpy as np
import pandas as pd

project_root = Path(__file__).parents[2]
sys.path.insert(0, str(project_root))

from utils import model_serving


def read_text(file):
    test_directory = Path(__file__).parent

    with open(test_directory / file, "rt", encoding="utf-8") as f_in:
        return f_in.read().strip()


def test_base64_decode():
    base64_input = read_text("data.b64")

    actual_result = model_serving.base64_decode(base64_input)
    expected_result = {
        "student": {
            "StudentID": 2566.0,
            "Age": 17.0,
            "Gender": 0.0,
            "Ethnicity": 0.0,
            "ParentalEducation": 0.5,
            "StudyTimeWeekly": 0.41918744404386094,
            "Absences": 0.3103448275862069,
            "Tutoring": 0.0,
            "ParentalSupport": 0.75,
            "Extracurricular": 0.0,
            "Sports": 0.0,
            "Music": 0.0,
            "Volunteering": 0.0,
        },
        "student_id": 2566.0,
    }
    assert actual_result == expected_result


class ScalerMock:
    def __init__(self, value):
        self.value = value

    def transform(self, X):
        n = len(X)
        return np.array([self.value] * n)


def test_preprocessing():

    scaler = ScalerMock(0.5)
    model_service = model_serving.ModelService(None, scaler)

    student = pd.DataFrame(
        [
            {
                "StudentID": 2566.0,
                "Age": 17.0,
                "Gender": 0.0,
                "Ethnicity": 0.0,
                "ParentalEducation": 0.5,
                "StudyTimeWeekly": 0.41918744404386094,
                "Absences": 0.3103448275862069,
                "Tutoring": 0.0,
                "ParentalSupport": 0.75,
                "Extracurricular": 0.0,
                "Sports": 0.0,
                "Music": 0.0,
                "Volunteering": 0.0,
            }
        ]
    )
    print(student)

    actual_features = model_service.preprocessing(student)

    expected_features = {
        "ParentalEducation": {0: 0.5},
        "StudyTimeWeekly": {0: 0.5},
        "Absences": {0: 0.5},
        "Tutoring": {0: 0.0},
        "ParentalSupport": {0: 0.5},
        "Extracurricular": {0: 0.0},
        "Sports": {0: 0.0},
        "Music": {0: 0.0},
        "Volunteering": {0: 0.0},
    }
    expected_features = pd.DataFrame(expected_features)
    assert all(actual_features == expected_features)


class ModelMock:
    def __init__(self, value):
        self.value = value

    def predict(self, X):
        n = len(X)
        return [self.value] * n


def test_predict():
    model_mock = ModelMock(4.0)
    model_service = model_serving.ModelService(model_mock, None)

    features = {
        "student": {
            "StudentID": 2566.0,
            "Age": 17.0,
            "Gender": 0.0,
            "Ethnicity": 0.0,
            "ParentalEducation": 0.5,
            "StudyTimeWeekly": 0.41918744404386094,
            "Absences": 0.3103448275862069,
            "Tutoring": 0.0,
            "ParentalSupport": 0.75,
            "Extracurricular": 0.0,
            "Sports": 0.0,
            "Music": 0.0,
            "Volunteering": 0.0,
        },
        "student_id": 2566.0,
    }

    actual_prediction = model_service.only_predict(features)
    expected_prediction = 4.0

    assert actual_prediction == expected_prediction


def test_lambda_handler():
    model_mock = ModelMock(4.0)
    scaler = ScalerMock(0.5)
    model_version = "Test123"
    model_service = model_serving.ModelService(model_mock, scaler, model_version)

    base64_input = read_text("data.b64")

    event = {
        "Records": [
            {
                "kinesis": {
                    "data": base64_input,
                },
            }
        ]
    }

    actual_predictions = model_service.lambda_handler(event)
    expected_predictions = {
        "predictions": [
            {
                "model": "student-performance",
                "version": model_version,
                "prediction": {"GPA": 4.0, "student_id": 2566.0},
            }
        ]
    }

    assert actual_predictions == expected_predictions
