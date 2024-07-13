# Student Performance

## Index

- [Problem Statement](#problem-statement)
    - [Dataset Source](#dataset-source)
    - [Project Objective](#project-objective)
    - [Project Implementation](#project-implementation)
    - [Technologies](#technologies)
- [Data Preprocessing and Model Training](#data-preprocessing-and-model-training)

## Problem Statement

### Dataset Source

The dataset used in this project is sourced from Kaggle: Students Performance Dataset.

### Project Objective

The primary goal of this project is to develop a predictive model for classifying students' grades into distinct categories. This classification leverages various features such as parental involvement, extracurricular activities, and academic performance. The insights gained from this model aim to provide guidelines for understanding and improving student outcomes.

### Project Implementation

This comprehensive approach ensures that the predictive model is well-maintained, scalable, and capable of providing valuable insights into student performance.

The project involves several key components:

1. **Training Pipeline:**

    - The training pipeline will be managed by an orchestrator.
    - Models and related artifacts will be saved to Amazon S3 for later use.

1. **Inference Pipeline:**

    - The saved models will be consumed by an inference pipeline for predictions.

1. **Monitoring and Maintenance:**

    - The project will include monitoring capabilities using Evidently.
    - Continuous Integration/Continuous Deployment (CI/CD) practices will be implemented.

1. **Infrastructure and Automation:**

    - Makefiles and Terraform will be used for automation and infrastructure management.
    - The project will include both unit and integration tests to ensure robustness and reliability.

### Technologies:

- **Python and Bash**
- **Git/GitHub**: Code versioning and CI/CD
- **MLFlow**: Model Tracking and Registry
- **AWS**: Cloud provider
    - **Lambda**: 
- **Terraform**: Infrastructure as Code (IaC)
- **Mage**: Training Orchestration Pipeline
- **Docker and docker-compose**: Create and Manage Containers
- **Evidently and Grafana**: Monitoring

## Data Preprocessing and Model Training

All this phase runs in Mage. 

More information about the decisions in [this notebook](research.ipynb)

It consists in 2 pipelines:
1. Data processing:
    - Demographic columns has been dropped to avoid bias in production due to the nature of these columns. Therefore, only the needed colums are kept.
    - Ordinal categorical columns (ParentalEducation, ParentalSupport) and numerical columns with uniform distribution (StudyTimeWeekly, Absences) are scaled using MinMaxScaler from sklearn. This scaler is saved in mlflow as an artifact for the run.
2. Model training:
    - Hyperparameter tuning in the training set
    - Best model selection with the validation set
    - Register the chosen model and save it to S3




    - MLFlow:
        - To the notebook in the terminal run: `mlflow server -h 127.0.0.1 -p 5000 --backend-store-uri sqlite:///mlflow_db/mlflow.db --default-artifact-root s3://mlflow-artifact-student-performance`

## Future steps
- Migrate Training Pipeline to cloud
- Model tracking and versioning to cloud
- Automatize the training when the data drifs surpasses a treshold