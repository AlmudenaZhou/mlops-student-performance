cd $(dirname $0)

docker-compose up -d

cd ..

source .venv/Scripts/activate

export TEST_RUN="True"

set -e

python monitoring/src/scripts/create_db.py
python monitoring/src/pipelines/adapt_data.py
python monitoring/src/pipelines/prepare_reference_data.py
python monitoring/src/pipelines/scheduler.py
