import os
import glob

from utils.model_serving import init_model_service_with_kinesis

root_dir = os.path.dirname(os.path.realpath(__file__))
# root_dir needs a trailing slash (i.e. /root/dir/)
for filename in glob.iglob(root_dir + '**/**', recursive=True):
    print(filename)

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

model_service = init_model_service_with_kinesis(
    prediction_stream_name=PREDICTIONS_STREAM_NAME, run_id=RUN_ID, test_run=TEST_RUN
)


def lambda_handler(event, _):

    return model_service.lambda_handler(event)
