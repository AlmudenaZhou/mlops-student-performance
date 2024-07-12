FROM python:3.10-slim

RUN pip install mlflow==2.12.1

EXPOSE 5000

CMD [ \
    "mlflow", "server", \
    "--backend-store-uri", "sqlite:///home/mlflow/mlflow.db", \
    "--default-artifact-root", "s3://mlflow-artifact-student-performance", \
    "--host", "0.0.0.0", \
    "--port", "5000", \
]