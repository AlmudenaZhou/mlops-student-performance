source .venv/Scripts/activate

export TEST_RUN="True"

set -e

rm -f data/reference/reference_data.parquet

python monitoring/src/scripts/drop_db.py
python monitoring/src/scripts/create_db.py
python monitoring/src/pipelines/scheduler.py
