# Student Performance

## Index

- [Problem Statement](#problem-statement)
    - [Dataset Source](#dataset-source)
    - [Project Objective](#project-objective)
    - [Project Implementation](#project-implementation)
    - [Technologies](#technologies)
- [Data Preprocessing and Model Training](#data-preprocessing-and-model-training)
- [Model Serving](#model-serving)

## Problem Statement

### Dataset Source

The dataset used in this project is sourced from [Kaggle: Students Performance Dataset](https://www.kaggle.com/datasets/rabieelkharoua/students-performance-dataset).

### Project Objective

The primary goal of this project is to develop a predictive model for classifying students' grades into distinct categories. This classification leverages various features such as parental involvement, extracurricular activities, and academic performance. The insights gained from this model aim to provide guidelines for understanding and improving student outcomes.

### Project Implementation

The project will be divided into several distinct components:

1. **Training Pipeline:**

    - The training pipeline will be managed by an orchestrator.
    - Models and related artifacts will be saved to Amazon S3 for later use.

1. **Inference Pipeline:**

    - The saved models will be consumed by an inference pipeline for predictions.
    - This can be done via Streaming or Flask Web Service. The one that will be deployed in the cloud 
    with the complete automatization will be the Streaming.
    - This part will be tested locally using Makefiles and 

1. **Monitoring and Maintenance:**

    - The project will include monitoring capabilities using Evidently along with Grafana

1. **Infrastructure and Automation:**

    - Terraform will be used for automation and infrastructure management.

1. **CI/CD workflows**
    - Code quality checks are included in the CI workflow to ensure a gold standard code.
    - The project will include both unit and integration tests in the CI workflow to ensure robustness and reliability to seamlessly deploy the code and container images to the cloud through the CD workflow.

### Technologies:

- **Python**: Coding
    - Dev libraries: black, pytest, isort, pylint
    - ML libraries: sklearn, pandas, numpy
- **Git and GitHub Actions**: Code versioning and CI/CD
- **MLFlow**: Model Tracking and Registry
- **AWS**: Cloud provider
    - **Lambda with ECR**: Model Serving
    - **Kinesis**: Event Streaming
    - **S3**: Data and MLFlow Artifact Path
    - **Others**: IAM, CloudWatch
- **Terraform**: Infrastructure as Code (IaC)
- **Mage**: Training Orchestration Pipeline
- **Docker and docker-compose**: Create and Manage Containers
- **Evidently and Grafana**: Monitoring
- **Other**: localstack, Makefile, pyproject.toml

## Data Preprocessing and Model Training

All this phase runs in Mage. 

More information about the decisions in [this notebook](research.ipynb)

It consists in 2 pipelines:
1. Data processing:
    - Demographic columns has been dropped to avoid bias in production due to the nature of these columns. Therefore, only the needed colums are kept.
    - Ordinal categorical columns (ParentalEducation, ParentalSupport) and numerical columns with uniform distribution (StudyTimeWeekly, Absences) are scaled using MinMaxScaler from sklearn. This scaler is saved in mlflow as an artifact for the run.
2. Model training:
    - Hyperparameter tuning in the training set for several models
    - Best model selection with the validation set, measured by f1-macro as there were unbalanced categories
    - Register the chosen model and save it to S3

### How to use:

1. Download the data from: https://www.kaggle.com/datasets/rabieelkharoua/students-performance-dataset
1. Place the csv in a folder named `data` in the project path and renamed it to `Student_performance_data.csv`
1. Configure the AWS credentials downloading an access token using the IAM. For more information read: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html
1. Add the secrets in the [mage io_config](orchestrator/student-performance/io_config.yaml) through the env or hardcoding them there. For more information: https://docs.mage.ai/production/deploying-to-cloud/secrets/AWS#working-with-secrets-in-mage
1. From the [orchestrator folder](orchestrator) run in the terminal `docker-compose up -d` to get the mlflow and mage servers running.
1. Enter `http://localhost:6789/` to see the mage ui. Optionally, you can enter to `http://localhost:5000/` to check if mlflow is running correctly
1. Inside Mage, go to pipelines and run first the preprocessing pipeline to generate the data for training the model
1. Run the model pipeline to save automatically the best model in the s3 bucket with its version and the preprocessing model, along with the results of all the experiments that have been done.
1. Check that the experiment folder `1` is in your S3
bucket.

## Model Serving

This will contained the inference pipeline. Once the model has been trained and saved, it's time to use it. This part is intended to retrieve the models from the S3 and receive an input and with both, predict the GPA for the user and send the result back. For this, 2 ways has been considered:

- **Web Service**: deploying a Flask app in an EC2, you can receive requests from users through its endpoint and send it back via frontend. This has been only developed locally and has not been deployed. However, can be a possibility to explore in the future.

- **Streaming**: using kinesis to handle the events from the users and to give back the response, this can be deployed using a serverless based on events architecture. This is the way that has been chosen for the final deployment of this project.


## Future steps
- Migrate Training Pipeline to cloud
- Deployment of the web service
- Added to the firts event streaming the web service?
- Automatize the training when the data drifs surpasses a treshold