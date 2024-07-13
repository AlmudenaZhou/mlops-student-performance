import os

import boto3
import pickle
import mlflow
from mlflow import MlflowClient
import pandas as pd


def load_models():

    BUCKET_NAME = os.getenv("BUCKET_NAME")
    RUN_ID = os.getenv("RUN_ID")
    ARTIFACT_FOLDER = os.getenv("ARTIFACT_FOLDER")
    MODEL_FOLDER = os.getenv("MODEL_FOLDER")
    MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")
    EXPERIMENT_ID = os.getenv("EXPERIMENT_ID")

    artefacts_uri = f's3://{BUCKET_NAME}/{EXPERIMENT_ID}/{RUN_ID}/artifacts'

    #model = load_model(artefacts_uri, MODEL_FOLDER)
    model = None

    scaler = load_scaler(artefacts_uri, MLFLOW_TRACKING_URI, RUN_ID, ARTIFACT_FOLDER)

    return model, scaler


def load_model(artefacts_uri, MODEL_FOLDER): 
    model_uri = f'{artefacts_uri}/{MODEL_FOLDER}'
    model = mlflow.pyfunc.load_model(model_uri)
    return model


def load_scaler(artefacts_uri, MLFLOW_TRACKING_URI, RUN_ID, ARTIFACT_FOLDER):
    artefacts_uri = artefacts_uri + f"/{ARTIFACT_FOLDER}/minmax_scaler.bin"
    artifact_path = os.path.join(ARTIFACT_FOLDER, "minmax_scaler.bin")

    if not os.path.exists(artifact_path):
        if MLFLOW_TRACKING_URI:
            client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)
            client.download_artifacts(run_id=RUN_ID, path=ARTIFACT_FOLDER, dst_path='.')
        else:
            s3 = boto3.resource('s3')
            parts = artefacts_uri.removeprefix('s3://').split('/', 1)
            bucket, key = parts

            os.makedirs(ARTIFACT_FOLDER, exist_ok=True)
            print(bucket, key)
            with open(artifact_path, 'wb') as data:
                s3.Bucket(bucket).download_fileobj(key, data)

    with open(artifact_path, "rb") as f_in:
        scaler = pickle.load(f_in)

    return scaler


def preprocessing(scaler, raw_data: pd.DataFrame):
    new_data = raw_data.copy()
    minmax_cols = ['ParentalEducation', 'StudyTimeWeekly',
                   'Absences', 'ParentalSupport']
    x_sc = scaler.transform(raw_data.loc[:, minmax_cols])
    new_data.loc[:, minmax_cols] = x_sc

    return new_data


def predict(model, scaler, raw_data):
    df_data = pd.DataFrame([raw_data])
    features = preprocessing(scaler, df_data)
    pred = model.predict(features)
    return float(pred[0])