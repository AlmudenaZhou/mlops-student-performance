import os
import json
import base64
import pickle
import logging

import boto3
import mlflow
import pandas as pd
from mlflow import MlflowClient

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(10)


def load_models(need_scaler):

    BUCKET_NAME = os.getenv("BUCKET_NAME")
    RUN_ID = os.getenv("RUN_ID")
    ARTIFACT_FOLDER = os.getenv("ARTIFACT_FOLDER")
    MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")
    EXPERIMENT_ID = os.getenv("EXPERIMENT_ID")
    MODEL_LOCATION = os.getenv("MODEL_LOCATION", "")

    scaler = None

    if MODEL_LOCATION:
        model_path = os.path.join(MODEL_LOCATION, "mlruns", "model.pkl")
        model = load_binary_file_from_local_path(model_path)

        if need_scaler:
            scaler_path = os.path.join(
                MODEL_LOCATION, "minmax_scaler", "minmax_scaler.bin"
            )
            scaler = load_binary_file_from_local_path(scaler_path)

        return model, scaler

    artefacts_uri = f"s3://{BUCKET_NAME}/{EXPERIMENT_ID}/{RUN_ID}/artifacts"

    print(artefacts_uri)
    model = load_model(artefacts_uri, "mlruns")

    if need_scaler:
        scaler = load_scaler(
            artefacts_uri, MLFLOW_TRACKING_URI, RUN_ID, ARTIFACT_FOLDER
        )

    return model, scaler


def load_model(artefacts_uri, MODEL_FOLDER):
    model_uri = f"{artefacts_uri}/{MODEL_FOLDER}"
    model = mlflow.pyfunc.load_model(model_uri)
    return model


def load_binary_file_from_local_path(file_path):
    with open(file_path, "rb") as f_in:
        content = pickle.load(f_in)

    return content


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

    scaler = load_binary_file_from_local_path(artifact_path)

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
        logger.info("ModelService initialized with model version: %s", model_version)

    def preprocessing(self, raw_data: pd.DataFrame):
        logger.info("Starting preprocessing")
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

        logger.info("Preprocessed data: %s", new_data.to_dict())
        return new_data

    def only_predict(self, features):
        pred = self.model.predict(features)
        logger.info("Prediction result: %f", float(pred[0]))
        return float(pred[0])

    def predict(self, raw_record):
        logger.info("Starting prediction for raw data: %s", raw_record)
        df_data = pd.DataFrame([raw_record])
        features = self.preprocessing(df_data)
        pred = self.only_predict(features)
        return pred

    def batch_predict(self, raw_data: pd.DataFrame):
        logger.info("Starting prediction for raw data. Head: %s", raw_data)
        features = self.preprocessing(raw_data)
        pred = self.only_predict(features)

        return pred

    def lambda_handler(self, event):
        logger.info("Lambda handler received event: %s", event)

        predictions_events = []

        for record in event["Records"]:
            encoded_data = record["kinesis"]["data"]
            logger.info("Encoded data from Kinesis: %s", encoded_data)
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
        logger.info("Prediction events: %s", predictions_events)

        return {"predictions": predictions_events}


class KinesisCallback:
    def __init__(self, kinesis_client, prediction_stream_name):
        self.kinesis_client = kinesis_client
        self.prediction_stream_name = prediction_stream_name
        logger.info(
            "Initialized KinesisCallback with stream name: %s", prediction_stream_name
        )

    def put_record(self, prediction_event):
        student_id = prediction_event["prediction"]["student_id"]
        logger.info("Adding Kinesis record for student ID: %s", student_id)
        try:
            response = self.kinesis_client.put_record(
                StreamName=self.prediction_stream_name,
                Data=json.dumps(prediction_event),
                PartitionKey=str(student_id),
            )
            logger.info("Kinesis record added with response: %s", response)
        except Exception as e:
            logger.error("Failed to add Kinesis record: %s", e, exc_info=True)


def create_kinesis_client():
    endpoint_url = os.getenv("KINESIS_ENDPOINT_URL")
    if endpoint_url is None:
        logger.info("Creating Kinesis client with default endpoint")
        return boto3.client("kinesis")
    logger.info("Creating Kinesis client with custom endpoint: %s", endpoint_url)
    return boto3.client("kinesis", endpoint_url=endpoint_url)


def init_model_service_with_kinesis(
    prediction_stream_name: str, run_id: str, test_run: bool
):
    logger.info("Initializing model service with run ID: %s", run_id)
    callbacks = []

    if not test_run:
        logger.info("Non-test run detected, setting up Kinesis callback")
        kinesis_client = create_kinesis_client()
        kinesis_callback = KinesisCallback(kinesis_client, prediction_stream_name)
        callbacks.append(kinesis_callback.put_record)

    model_service = init_model_service(model_version=run_id, callbacks=callbacks, need_scaler=True)

    return model_service


def init_model_service(model_version=None, callbacks=None, need_scaler=False):

    model, scaler = load_models(need_scaler)
    logger.info("Models loaded successfully")

    model_service = ModelService(
        model=model, scaler=scaler, model_version=model_version, callbacks=callbacks
    )
    logger.info("Model service initialized with version: %s", model_version)

    return model_service
