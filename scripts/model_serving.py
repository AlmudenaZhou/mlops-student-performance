import base64
import json
import os
import pickle

import boto3
import mlflow
import pandas as pd
from mlflow import MlflowClient


def load_models():

    BUCKET_NAME = os.getenv("BUCKET_NAME")
    RUN_ID = os.getenv("RUN_ID")
    ARTIFACT_FOLDER = os.getenv("ARTIFACT_FOLDER")
    MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")
    EXPERIMENT_ID = os.getenv("EXPERIMENT_ID")

    artefacts_uri = f"s3://{BUCKET_NAME}/{EXPERIMENT_ID}/{RUN_ID}/artifacts"

    print(artefacts_uri)
    model = load_model(artefacts_uri, "mlruns")

    scaler = load_scaler(artefacts_uri, MLFLOW_TRACKING_URI, RUN_ID, ARTIFACT_FOLDER)

    return model, scaler


def load_model(artefacts_uri, MODEL_FOLDER):
    model_uri = f"{artefacts_uri}/{MODEL_FOLDER}"
    model = mlflow.pyfunc.load_model(model_uri)
    return model


def load_scaler(artefacts_uri, MLFLOW_TRACKING_URI, RUN_ID, ARTIFACT_FOLDER):
    artefacts_uri = artefacts_uri + f"/{ARTIFACT_FOLDER}/minmax_scaler.bin"
    artifact_path = os.path.join(ARTIFACT_FOLDER, "minmax_scaler.bin")

    if not os.path.exists(artifact_path):
        if MLFLOW_TRACKING_URI:
            client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)
            client.download_artifacts(run_id=RUN_ID, path=ARTIFACT_FOLDER, dst_path=".")
        else:
            s3 = boto3.resource("s3")
            parts = artefacts_uri.removeprefix("s3://").split("/", 1)
            bucket, key = parts

            os.makedirs(ARTIFACT_FOLDER, exist_ok=True)
            print(bucket, key)
            with open(artifact_path, "wb") as data:
                s3.Bucket(bucket).download_fileobj(key, data)

    with open(artifact_path, "rb") as f_in:
        scaler = pickle.load(f_in)

    return scaler


def base64_decode(encoded_data):
    decoded_data = base64.b64decode(encoded_data).decode("utf-8")
    ride_event = json.loads(decoded_data)
    return ride_event


class ModelService:
    def __init__(self, model, scaler, model_version=None, callbacks=None):
        self.model, self.scaler = model, scaler
        self.model_version = model_version
        self.callbacks = callbacks or []

    def preprocessing(self, raw_data: pd.DataFrame):
        new_data = raw_data.copy()
        minmax_cols = [
            "ParentalEducation",
            "StudyTimeWeekly",
            "Absences",
            "ParentalSupport",
        ]
        x_sc = self.scaler.transform(raw_data.loc[:, minmax_cols])
        new_data.loc[:, minmax_cols] = x_sc

        columns_to_drop = ["StudentID", "Age", "Gender", "Ethnicity"]
        new_data.drop(columns_to_drop, axis=1, inplace=True)

        print(new_data.to_dict())
        return new_data

    def only_predict(self, features):
        pred = self.model.predict(features)
        return float(pred[0])

    def predict(self, raw_data):
        df_data = pd.DataFrame([raw_data])
        print(df_data)
        features = self.preprocessing(df_data)
        pred = self.only_predict(features)
        return pred

    def lambda_handler(self, event):

        predictions_events = []

        for record in event["Records"]:
            encoded_data = record["kinesis"]["data"]
            print(encoded_data)
            student_event = base64_decode(encoded_data)

            student = student_event["student"]
            student_id = student_event["student_id"]

            prediction = self.predict(student)

            prediction_event = {
                "model": "student-performance",
                "version": self.model_version,
                "prediction": {"GPA": prediction, "student_id": student_id},
            }

            for callback in self.callbacks:
                callback(prediction_event)

            predictions_events.append(prediction_event)
        print(predictions_events)

        return {"predictions": predictions_events}


class KinesisCallback:
    def __init__(self, kinesis_client, prediction_stream_name):
        self.kinesis_client = kinesis_client
        self.prediction_stream_name = prediction_stream_name

    def put_record(self, prediction_event):
        studemt_id = prediction_event["prediction"]["student_id"]

        self.kinesis_client.put_record(
            StreamName=self.prediction_stream_name,
            Data=json.dumps(prediction_event),
            PartitionKey=str(studemt_id),
        )


def create_kinesis_client():
    endpoint_url = os.getenv("KINESIS_ENDPOINT_URL")

    if endpoint_url is None:
        return boto3.client("kinesis")

    return boto3.client("kinesis", endpoint_url=endpoint_url)


def init_model_service(prediction_stream_name: str, run_id: str, test_run: bool):

    callbacks = []

    if not test_run:
        kinesis_client = create_kinesis_client()
        kinesis_callback = KinesisCallback(kinesis_client, prediction_stream_name)
        callbacks.append(kinesis_callback.put_record)

    model, scaler = load_models()

    model_service = ModelService(
        model=model, scaler=scaler, model_version=run_id, callbacks=callbacks
    )

    return model_service
