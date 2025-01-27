# pylint: disable=duplicate-code
import os
import glob
import json

import requests
from deepdiff import DeepDiff

with open("kinesis_event.json", "rt", encoding="utf-8") as f_in:
    event = json.load(f_in)

root_dir = os.path.dirname(os.path.realpath(__file__))
# root_dir needs a trailing slash (i.e. /root/dir/)
for filename in glob.iglob(root_dir + '**/**', recursive=True):
    print(filename)

url = "http://localhost:8080/2015-03-31/functions/function/invocations"
actual_response = requests.post(url, json=event, timeout=10).json()
print("actual response:")

print(json.dumps(actual_response, indent=2))


expected_response = {
    "predictions": [
        {
            "model": "student-performance",
            "version": "Test123",
            "prediction": {"GPA": 2.0, "student_id": 2566.0},
        }
    ]
}


diff = DeepDiff(actual_response, expected_response, significant_digits=1)
print(f"diff={diff}")

assert "type_changes" not in diff
assert "values_changed" not in diff
