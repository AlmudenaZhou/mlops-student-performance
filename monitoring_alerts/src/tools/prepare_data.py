from typing import Tuple

import pandas as pd
import pandas as pd
from evidently.test_preset import DataDriftTestPreset
from evidently.test_suite import TestSuite


def calculate_data_drift() -> Tuple[bool, str, bytes]:
    """
    Returns:
        True/False whether alert is detected
    """

    num_features = [
        'ParentalEducation',
        'StudyTimeWeekly',
        'Absences',
        'ParentalSupport',
    ]
    cat_features = ['Tutoring', 'Extracurricular', 'Sports', 'Music', 'Volunteering']

    # Prepare reference data
    DATA_REF_DIR = "data/reference"
    ref_path = f"{DATA_REF_DIR}/reference_data.parquet"
    ref_data = pd.read_parquet(ref_path)
    columns = num_features + cat_features
    reference_data = ref_data.loc[:, columns]

    DATA_FEATURES_DIR = "data/features"

    # Get current data (features)
    current_data_path = f"{DATA_FEATURES_DIR}/processed_val.parquet"
    current_data = pd.read_parquet(current_data_path)
    current_data = current_data.loc[:, columns] + 3

    data_drift = TestSuite(
        tests=[
            DataDriftTestPreset(),
        ]
    )

    data_drift.run(reference_data=reference_data, current_data=current_data)

    from monitoring_alerts.src.tools.helper_functions import get_evidently_html

    html, html_bytes = get_evidently_html(data_drift)

    test_summary = data_drift.as_dict()
    other_tests_summary = []

    failed_tests = []
    for test in test_summary["tests"]:
        if test["status"].lower() == "fail":
            failed_tests.append(test)

    is_alert = any([failed_tests, other_tests_summary])
    print(f"Alert Detected: {is_alert}")

    return is_alert, html, html_bytes
