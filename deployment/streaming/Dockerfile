FROM public.ecr.aws/lambda/python:3.9

RUN pip install -U pip

COPY requirements.txt .

RUN pip install -r requirements.txt

WORKDIR /app

COPY deployment/streaming/lambda_function.py .
COPY utils/ ./utils

ENV PYTHONPATH="${PYTHONPATH}:/app"

CMD [ "lambda_function.lambda_handler" ]
