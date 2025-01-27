#!/usr/bin/env bash

if [[ -z "${GITHUB_ACTIONS}" ]]; then
  cd "$(dirname "$0")"
fi

# Calculate the absolute path to the project root directory
cd "../.."

if [ "${LOCAL_IMAGE_NAME}" == "" ]; then
    export LOCAL_IMAGE_NAME="student-performance"
    echo "LOCAL_IMAGE_NAME is not set, building a new image with tag ${LOCAL_IMAGE_NAME}"
    docker build -t ${LOCAL_IMAGE_NAME} -f deployment/streaming/Dockerfile .
else
    echo "no need to build image ${LOCAL_IMAGE_NAME}"
fi

cd "tests/integration_tests/"
echo "Changed to integration_tests folde"

export PREDICTIONS_STREAM_NAME="student-performance"
export AWS_DEFAULT_REGION="eu-west-1"

docker-compose up -d

echo "finished docker-compose up"
sleep 5

aws --endpoint-url=http://localhost:4566 \
    kinesis create-stream \
    --stream-name ${PREDICTIONS_STREAM_NAME} \
    --shard-count 1

echo "Kinesis Stream created"

echo "Start running test_docker.py"

python test_docker.py

ERROR_CODE=$?

if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE}
fi

echo "Start running test_kinesis.py"
python test_kinesis.py

ERROR_CODE=$?

if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE}
fi


docker-compose down
