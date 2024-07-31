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

cd $(dirname $0)

docker-compose up -d

sleep 5

aws --endpoint-url=http://localhost:4566 \
    kinesis create-stream \
    --stream-name ${INPUT_STREAM_NAME} \
    --shard-count 1

python test_docker.py

ERROR_CODE=$?

if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE}
fi


python test_kinesis.py

ERROR_CODE=$?

if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE}
fi


docker-compose down
