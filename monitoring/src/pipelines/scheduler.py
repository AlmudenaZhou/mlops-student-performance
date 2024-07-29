import os
from typing import Text

import pendulum
from prefect import flow

from monitoring.src.pipelines.predict import predict
from monitoring.src.pipelines.monitor_data import monitor_data
from monitoring.src.pipelines.monitor_model import monitor_model


@flow()
def scheduled_flow(start_date: Text, end_date: Text, interval: int = 60) -> None:
    """
    Runs a scheduled flow for predicting and monitoring student performance

    Args:
        start_date (Text):
            A string representing the start date and time of the flow,
            in ISO 8601 format.
        end_date (Text):
            A string representing the end date and time of the flow,
            in ISO 8601 format.
            If None, the flow will run indefinitely.
        interval:
            An integer representing the interval,
            in minutes, between predictions.
    Raises:
        ValueError: If start_date is not a valid ISO 8601 date or time string.

    Example:
        >>> scheduled_flow('2023-04-06T00:00:00Z', '2023-04-07T00:00:00Z', 30)
    """

    start = pendulum.parse(start_date)
    end = pendulum.parse(end_date)
    ts = start

    while ts < end:

        print(ts)

        # Run data quality monitoring pipeline
        # Run prediction pipeline
        predict(ts, interval)

        # Run data quality monitoring pipeline
        monitor_data(ts, interval)

        # Run model performance monitoring pipeline
        ts_previous = ts.subtract(minutes=interval)

        #   Start from second period to make sure that
        # we have 'predictions' for ts_previous.
        if ts_previous > start:
            monitor_model(ts_previous, interval)

        ts = ts.add(minutes=interval)


if __name__ == "__main__":

    TEST_RUN = os.getenv("TEST_RUN", "False") == "True"

    if TEST_RUN:
        from dotenv import load_dotenv

        load_dotenv()

    START_DATE_TIME = '2024-07-28 13:54:00'
    END_DATE_TIME = '2024-07-28 19:51:00'
    BATCH_INTERVAL = 15

    scheduled_flow(
        start_date=START_DATE_TIME, end_date=END_DATE_TIME, interval=BATCH_INTERVAL
    )
