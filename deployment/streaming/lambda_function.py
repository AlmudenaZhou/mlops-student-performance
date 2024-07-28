import os

from utils.model_serving import init_model_service

TEST_RUN = os.getenv("TEST_RUN", "False") == "True"

if TEST_RUN:
    MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", None)

    from dotenv import load_dotenv

    load_dotenv()

    if MLFLOW_TRACKING_URI is not None:
        os.environ["MLFLOW_TRACKING_URI"] = MLFLOW_TRACKING_URI

RUN_ID = os.getenv("RUN_ID")
EXPERIMENT_NAME = os.getenv("EXPERIMENT_NAME")

PREDICTIONS_STREAM_NAME = os.getenv("PREDICTIONS_STREAM_NAME", "student-performance")

model_service = init_model_service(
    prediction_stream_name=PREDICTIONS_STREAM_NAME, run_id=RUN_ID, test_run=TEST_RUN
)


def lambda_handler(event, _):

    model_service.lambda_handler(event)
