import os
from pathlib import Path

import pandas as pd

from utils.model_serving import init_model_service
from monitoring.src.utils.utils import prepare_scoring_data

TEST_RUN = os.getenv("TEST_RUN", "False") == "True"

if TEST_RUN:
    from dotenv import load_dotenv

    load_dotenv()


def prepare_reference_dataset():
    """Prepare reference dataset for the monitoring"""

    DATA_FEATURES_DIR = "data/features"
    target_col = "GradeClass"
    prediction_col = "predictions"

    print("Load data")
    path = f"{DATA_FEATURES_DIR}/processed_train.parquet"
    data = pd.read_parquet(path)
    data = data.sample(frac=0.3)

    data = data.set_index("Timestamp")
    data = data.sort_index()
    print("Predictions generation")
    predictions_df = data.loc[:, ["uuid", target_col]]

    scoring_data = prepare_scoring_data(data)

    model_service = init_model_service()
    predictions_df[prediction_col] = model_service.only_predict(scoring_data)

    print("Save reference dataset")
    REFERENCE_DATA_DIR = Path("data/reference")
    REFERENCE_DATA_DIR.mkdir(exist_ok=True)
    path = REFERENCE_DATA_DIR / "reference_data.parquet"

    df = pd.concat([predictions_df, scoring_data], axis=1)
    df.to_parquet(path)


if __name__ == "__main__":

    prepare_reference_dataset()
