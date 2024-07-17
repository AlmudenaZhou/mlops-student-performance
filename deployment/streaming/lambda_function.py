import os
import json
import boto3
import base64

from scripts.model_serving import load_models, predict


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
kinesis_client = boto3.client('kinesis')

PREDICTIONS_STREAM_NAME = os.getenv('PREDICTIONS_STREAM_NAME', 'ride_predictions')


def prepare_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features


def lambda_handler(event, context):
    
    predictions_events = []
    
    for record in event['Records']:
        encoded_data = record['kinesis']['data']
        decoded_data = base64.b64decode(encoded_data).decode('utf-8')
        student = json.loads(decoded_data)

        ride = ride_event['ride']
        ride_id = ride_event['ride_id']
    
        features = prepare_features(ride)
        prediction = predict(features)
    
        prediction_event = {
            'model': 'ride_duration_prediction_model',
            'version': '123',
            'prediction': {
                'ride_duration': prediction,
                'ride_id': ride_id   
            }
        }

        if not TEST_RUN:
            kinesis_client.put_record(
                StreamName=PREDICTIONS_STREAM_NAME,
                Data=json.dumps(prediction_event),
                PartitionKey=str(ride_id)
            )
        
        predictions_events.append(prediction_event)

    return {
        'predictions': predictions_events
    }
