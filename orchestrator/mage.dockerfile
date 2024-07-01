FROM mageai/mageai:latest

ARG USER_CODE_PATH=/home/src/

RUN pip install -r ${USER_CODE_PATH}requirements.txt
