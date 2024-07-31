# Student Performance

## Index

- [Problem Statement](#problem-statement)
    - [Dataset Source](#dataset-source)
    - [Project Objective](#project-objective)
    - [Project Implementation](#project-implementation)
    - [Technologies](#technologies)
- [Data Preprocessing and Model Training](#data-preprocessing-and-model-training)
- [Inference Pipeline: Model Serving](#inference-pipeline-model-serving)
- [Monitoring: Model Maintenance](#monitoring-model-maintenance)
- [Infrastructure and Automation: Terraform, Infrastructure as Code](#infrastructure-and-automation-terraform-infrastructure-as-code)
- [Good Practices](#good-practices)
    - [Linter and Code Formatters](#linter-and-code-formatters)
    - [Makefile](#makefile)
    - [Precommit hooks](#precommit-hooks)
    - [Tests](#tests)
        - [Unit tests](#unit-tests)
        - [Integration tests](#integration-tests)
- [CI/CD pipeline](#cicd-pipeline)
- [Future steps](#future-steps)


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

1. **Monitoring:**

    - The project will include monitoring capabilities using Evidently along with Grafana

1. **Infrastructure and Automation:**

    - Terraform will be used for automation and infrastructure management.

1. **CI/CD workflows**
    - Code quality checks are included in the [CI workflow to ensure] a gold standard code.
    - The project will include both unit and integration tests in the [CI workflow to ensure] robustness and reliability to seamlessly deploy the code and container images to the cloud through the CD workflow.

**Before start**:

- It's mandatory to set the virtual environment

To create it:
```
python -m venv .venv
```
You can also do it through VS Code


To activate it and add the project path to the PYTHONPATH:

In Linux:
```
source .venv/Scripts/activate
echo "export PYTHONPATH=$PWD" >> .venv/Scripts/activate
pip install -r requirements.txt
```

In Windows CMD:
```
activate.bat
echo set PYTHONPATH=%CD% >> .venv\Scripts\activate.bat
```

To install the dependencies:
```
pip install -r requirements.txt
pip install -r monitoring_requirements.txt
```


- I have added an example.env with the environment variable names and a brief explanation. The program is expecting them to be filled in a new file called `.env`.

- Configure the AWS credentials downloading an access token using the IAM. For more information read: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html. You can set the credentials adding them to the AWS CLI configuration or from the .env individually to each service. I recommend the first one, as it's easier for using it locally with the scripts.



### Technologies:

- **Python and Shell Script**: Programming
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
- **Other**: localstack, Makefile, pyproject.toml, Pre-commit

## Data Preprocessing and Model Training

All this phase runs in Mage.

More information about the de[cisions in [this] notebook](research.ipynb)

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
1. Here the AWS credentials will be needed to be able to connect to it with mage.
1. Add the secrets in the [mage io_config](orchestrator/student-performance/io_config.yaml) through the env or hardcoding them there. For more information: https://docs.mage.ai/production/deploying-to-cloud/secrets/AWS#working-with-secrets-in-mage
1. From the [orchestrator folder](orchestrator) run in the terminal `docker-compose up -d` to get the mlflow and mage servers running.
1. Enter `http://localhost:6789/` to see the mage ui. Optionally, you can enter to `http://localhost:5000/` to check if mlflow is running correctly
1. Inside Mage, go to pipelines and run first the preprocessing pipeline to generate the data for training the model
1. Run the model pipeline to save automatically the best model in the s3 bucket with its version and the preprocessing model, along with the results of all the experiments that have been done.
1. Check that the experiment folder `1` is in your S3 bucket.

## Inference Pipeline: Model Serving

This will contained the inference pipeline. Once the model has been trained and saved, it's time to use it. This part is intended to retrieve the models from the S3 and receive an input and with both, predict the GPA for the user and send the result back. For this, 2 ways has been considered:

- **Web Service**: deploying a Flask app in an EC2, you can receive requests from users through its endpoint and send it back via frontend. This has been only developed locally and has not been deployed. However, can be a possibility to explore in the future.

    To deploy it in local: `make run_flask`

    To deploy it in local using mlflow experiment tracking: `make run_flask_with_mlflow`

    And to test it locally: `make run_web_test`

- **Streaming**: using kinesis to handle the events from the users and to give back the response, this can be deployed using a serverless based on events architecture.

    This is the way that has been chosen for the final deployment of this project. For this, the lambda of the deployment code has been dockerized to be able to easily deploy in the cloud. [Dockerfile](deployment/streaming/Dockerfile). It's deployed along with the utils dependencies.

    This is run and tested in: [Integration tests](#integration-tests)

In both cases, the scaler and model is obtained from the model registry developed in the Research and uploaded to the S3. And in both cases, it can be done through mlflow or using boto3 to avoid the need of uploading the database to load the artifacts.

## Monitoring: Model Maintenance

This module is the base for deploying a monitoring system for data drift in production along with the model, and trigger alerts to retrain the model.

To do the dashboard monitoring I used Grafana for the dashboards, Evidently for metrics calculations, Prefect for orchestration and Postgres as database.

For the alerts I used Evidently for the triggers and SES to send emails.

### Dashboards

This consist in 2 parts:
- Calculate and store the reference data from the training set. [prepare_reference_data.py](monitoring/src/pipelines/prepare_reference_data.py)
- Monitoring the incoming batch data:
    - **Data Pipeline**: compare the input data to the reference data, calculate metrics and plot the report.
    - **Model Pipeline**: calculate the predictions, compare them to the target, calculate metrics about the comparison and plot the dasboards


To perform datetime operations here, I had to implement a data adaptation where I join the x, y and added a synthetic timestamp with a generated uuid for each row.

#### Results

This results has been calculated using the validation dataset, using batches of 15min which are composed by 15 records. In the analysis of these dashboards, there are two main things to take into account: there will be a lot of false positives and negatives due to the lack of samples and the model has not been trained thoroughly and consequently, the predictions will not be reliable.

![image](img/dataset_drift.png)

![image](img/prediction_drift.png)

![image](img/target_drift.png)

The features has a big percentage of drifted ones. This can be due to the lack of samples. But if not, it can be beneficial to review it carefully.

As we can see in the panels, the predictions have drifted a lot, while the target drift is not significant.

More details and the How to use: [monitoring README file](monitoring/README.md#code-modules)


### Alerts

The alerts are programmed to be a cycle. When new batch of input data arrives, the pipeline is triggered. This new data must be already processed to be compared to the data saved as reference. This comparison is done via Evidently Tests, that can trigger the alerts if drift is detected. The alert calls the SES service to send to a list of recipients an alert of drift.

The initial implementation have static data and uses the same reference data and current data as the previous section. The SES is mocked through localstack and the important variables with sensible information, such as emails, are saved in the .env.

#### How to use it
1. Check the .env variables SENDER_EMAIL, RECIPIENT_LIST, PROJECT_NAME and LINK_URL are correctly filled.
From the monitoring_alerts folder:
1. `docker-compose up` to deploy the localstack SES

From the project folder:
1. `make run_monitoring_alert` this will verify as sender the `SENDER_EMAIL`, run the main monitoring alert code and check if the email has been correctly send.

For this demo, I added +3 purposely to the validation data to trigger the drift

Example mail:

![img](img/mail_example.png)

## Infrastructure and Automation: Terraform, Infrastructure as Code

The infrastructure of the project deployment will be done using Terraform. This will allow us to automate the deployment and deletion of the resources.

### Development Environments
I used 2 configurations:
- **stage**: test the changes here first
- **production**: resources to point for the real product

This is done as a good practice for not breaking the production environment. Usually, as the project is more relevant, the number of configurations increase adding some extra such local and dev. Here I decided to only use one for simplicity.

### Modules
The infrastructure is composed by 4 modules:

- **ecr**: saves the image for the lambda function into ECR. In the main.tf of this module, the image build code by default is for Linux systems. However, if you are running it on Windows, you need to swap the function with the code commented below.
- **kinesis**: created 2 kinesis streams, one for the inputs and another for the outputs.
- **lambda**: generates the iam role for using the kinesis services and the lambda service using the input kinesis stream as trigger, the ecr image and the previous iam role.
- **s3**: bucket for saving the mlflow artifacts

### How to use:
1. Check the aws credentials are well configured
1. You need to comment from [main.tf](infrastructure/main.tf) the first block: `terraform`, as you don't have any .tfstate generated yet.
1. Run `terraform init`, `terraform plan -var-file=vars/{config_name}.tfvars` and `terraform apply -var-file=vars/{config_name}.tfvars` where config_name is stg or prod.

    This should print on your terminal (the names will depend on your names at the .tfvars):

    ![img](img/terraform_apply_output.png)



1. Create a S3 bucket and upload the `terraform.tfstate` generated in the previous step and renamed it to `prod-terraform.tfstate` or `stg-terraform.tfstate` depending on what you run as config_name.
1. Uncomment the terraform block from [main.tf](infrastructure/main.tf) and change the bucket, key and region to match your bucket.
1. Test the new configuration running again the third step.


## Good Practices

### Linter and Code Formatters

I used isort and black as code formatters for a first automatic changes in ordered imports and standard clean code, respectively, and pylint as the linter for ensuring gold standard code.

They are triggered running in the terminal:
```
isort .
black .
pylint --recursive=y .
```

This must be done after having created and activated the environment

### Makefile

The makefile usually is used for compiled languages to avoid memorizing large commands and connect the file to compile to the file generated. Make compares automatically if the dependencies has a date later in time than the generated file, and if so it will run the query again.

This project is done based on python. Therefore, that functionality is not needed. However, trying to run all the queries, particularly in windows, I realized that I had to memorize a lot of commands and it would be easier to have all the commads centralized.

**The Makefile only stores the commands for the inference pipeline and is written to be run in Command Window in Windows**.

For using it, ensure that you have the venv correctly set and that the PATH_TO_GIT_BASH variable at the beginning of the Makefile is the same as yours.

[Makefile](Makefile)

### Precommit hooks

The pre-commit hooks will be used to ensure the quality of the code before the code is pushed to the repository. This can also be done through github actions, but I de[cided to use] the pre-commit hooks here to test it easier before pushing it.

By default, the pre-commit install downloads only the precommit hook, place in .git/hooks/pre-commit. However, since I am running the tests and pylint here, I de[cided to use] only the hook-type pre-push for the majority of the implemented hooks due to the large execution time.

#### Steps

1. Adds the pre-commit and pre-push needed to the .git local folder
```
pre-commit install --hook-type pre-commit --hook-type pre-push
```
2. For testing:
```
pre-commit run --all-files --hook-stage pre-push
```
Note: In Windows the pytest hook throws an error if `bash` is not recognized as a command in the terminal. To avoid this, I implemented:
`make run_precommit_push`

### Tests

#### Unit tests

This module is intended to ensure the correct functionality of the [model_serving module](utils/model_serving.py). Specifically the ModelServing class. [test_model.py](tests/unit_tests/test_model.py)

For accomplish this I implemented several tests:
- test_base64_decode: test the decode, as kinesis encodes the input data
- test_preprocessing: mocking the scaler, I test if the ModelService returns the expected output.
- test_predict: mocking the model, it tests if the predict method works correctly
- test_lambda_handler: tests the lambda handler, mocking the scaler and the model and running all the workflow.

This can be run using:

Windows:
`make run_unit_tests`

`(export PYTHONPATH=.&&python -m pytest .\tests\unit_tests\)`
It's important to add the project path to the PYTHONPATH due to the folder distribution.

#### Integration tests

The system receives the input data from kinesis, pass it to a lambda function, and this lambda returns the prediction to another kinesis stream. This connections between services needs to be tested, and that's what we are going to do here.

This part is divided in two:
- [test_docker](tests/integration_tests/test_docker.py): tests the lambda deployed in the container. It posts the [kinesis_event](tests/integration_tests/kinesis_event.json) to the input stream in kinesis, run the lambda and wait for the response.
- [test_kinesis](tests/integration_tests/test_kinesis.py): after running the lambda, test if the kinesis stream received the prediction event

For testing this seamlessly, I developed a shell script: [run.sh](tests/integration_tests/run.sh). This runs the following workflow:

1. If no LOCAL_IMAGE is passed, it builds the Dockerfile from deployment/streaming
1. Activates the venv
1. Run the docker-compose that creates or run the localstack (kinesis) and lambda containers
1. Create the Input Kinesis Stream
1. Runs test_docker and test_kinesis

Notes: special attention about the location of the files. The project is used for the Dockerfile build to avoid problems with the COPY. Additionally, it uses the docker-compose.yaml, .venv folder and Dockerfile which are in different files.

For running this in Windows:
`make run_integration_tests`

## CI/CD pipeline



## Future steps
- Migrate Training Pipeline to cloud
- Deployment of the web service
- Added to the firts event streaming the web service
- Automatize the training when the data drifs surpasses a treshold, instead of only alert
- Deploy the monitoring module
- Finish dynamic data ingestion in the monitoring module
- Finish complete integration between dashboard monitoring and alerts
