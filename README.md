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

The dataset for this project is sourced from [Kaggle: Students Performance Dataset](https://www.kaggle.com/datasets/rabieelkharoua/students-performance-dataset).

### Project Objective

The primary goal of this project is to develop a predictive model to classify students' grades into distinct categories. This classification will leverage various features such as parental involvement, extracurricular activities, and academic performance. The insights gained from this model aim to provide guidelines for understanding and improving student outcomes.

### Project Implementation

The project is divided into several components:

1. **Training Pipeline:**
    - Managed by an orchestrator, Mage.
    - Models and related artifacts will be saved to Amazon S3 for later use.

2. **Inference Pipeline:**
    - Consumes the saved models for predictions.
    - Can be implemented via Streaming or Flask Web Service. The Streaming method will be deployed in the cloud with full automation.
    - This part will be tested locally using Makefiles.

3. **Monitoring:**
    - Includes monitoring capabilities using Evidently and Grafana.

4. **Infrastructure and Automation:**
    - Terraform will be used for automation and infrastructure management.

5. **CI/CD Workflows:**
    - Includes code quality checks in the CI workflow to ensure high-quality code.
    - Incorporates both unit and integration tests in the CI workflow to ensure robustness and reliability, facilitating seamless deployment of code and container images to the cloud via the CD workflow.

### Before You Start

1. **Set Up the Virtual Environment:**

    1. To create the virtual environment:
        ```bash
        python -m venv .venv
        ```
        You can also set it up through VS Code.

    1. To activate it and add the project path to the PYTHONPATH:

        - In Linux:
        ```bash
        source .venv/bin/activate
        echo "export PYTHONPATH=$PWD" >> .venv/bin/activate
        pip install -r requirements.txt
        ```

        - In Windows CMD:
        ```cmd
        .venv\Scripts\activate.bat
        echo set PYTHONPATH=%CD% >> .venv\Scripts\activate.bat
        ```

    1. **Install Dependencies:**
        ```bash
        pip install -r requirements.txt
        pip install -r monitoring_requirements.txt
        ```

1. **Set Up Environment Variables:**

    - An `example.env` file is provided with the environment variable names and brief explanations. Fill these in a new file called `.env`.

1. **Configure AWS Credentials:**

    - Download an access token using AWS IAM. For more information, read the [AWS IAM guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html). You can set the credentials either by adding them to the AWS CLI configuration or by specifying them individually for each service in the `.env` file. The first method is recommended for easier local script usage.


### Technologies

- **Python and Shell Script**: Programming
  - Dev libraries: `black`, `pytest`, `isort`, `pylint`
  - ML libraries: `sklearn`, `pandas`, `numpy`
- **Git and GitHub Actions**: Code versioning and CI/CD
- **MLFlow**: Model tracking and registry
- **AWS**: Cloud provider
  - **Lambda with ECR**: Model serving
  - **Kinesis**: Event streaming
  - **S3**: Data and MLFlow artifact storage
  - **Others**: IAM, CloudWatch
- **Terraform**: Infrastructure as Code (IaC)
- **Mage**: Training orchestration pipeline
- **Docker and docker-compose**: Create and manage containers
- **Evidently and Grafana**: Monitoring
- **Other**: LocalStack, Makefile, `pyproject.toml`, Pre-commit

## Data Preprocessing and Model Training

All preprocessing and model training runs in Mage. For more details, refer to the [research notebook](research.ipynb).

### Pipelines

1. **Data Processing:**
    - Demographic columns are dropped to avoid bias in production, keeping only the necessary columns.
    - Ordinal categorical columns (e.g., `ParentalEducation`, `ParentalSupport`) and numerical columns with uniform distribution (e.g., `StudyTimeWeekly`, `Absences`) are scaled using `MinMaxScaler` from `sklearn`. The scaler is saved in MLFlow as an artifact for the run.

2. **Model Training:**
    - Hyperparameter tuning is performed on the training set for several models.
    - The best model is selected based on validation set performance, measured by `f1-macro` due to unbalanced categories.
    - The chosen model is registered and saved to S3.

### How to Use

1. **Download the Data:**
    - Download the dataset from [Kaggle: Students Performance Dataset](https://www.kaggle.com/datasets/rabieelkharoua/students-performance-dataset).
    - Place the CSV file in a folder named `data` in the project directory and rename it to `Student_performance_data.csv`.

2. **Set Up AWS Credentials:**
    - AWS credentials are needed to connect with Mage.
    - Add the secrets in the [Mage io_config](orchestrator/student-performance/io_config.yaml) via environment variables or by hardcoding them. For more information, refer to the [Mage documentation](https://docs.mage.ai/production/deploying-to-cloud/secrets/AWS#working-with-secrets-in-mage).

3. **Run Docker Compose:**
    - From the [orchestrator folder](orchestrator), run the following command in the terminal to start the MLFlow and Mage servers:
      ```bash
      docker-compose up -d
      ```

4. **Access Mage and MLFlow:**
    - Visit `http://localhost:6789/` to access the Mage UI.
    - Optionally, visit `http://localhost:5000/` to check if MLFlow is running correctly.

5. **Run Pipelines in Mage:**
    - In Mage, go to pipelines and run the preprocessing pipeline to generate data for training the model.
    - Run the model pipeline to save the best model automatically in the S3 bucket, along with its version, the preprocessing model, and the results of all experiments.

6. **Verify S3 Bucket:**
    - Ensure that the experiment folder `1` is present in your S3 bucket.


## Inference Pipeline: Model Serving

The inference pipeline utilizes the trained and saved model to predict the GPA for users based on their input. This section outlines two methods for deploying the inference pipeline: Web Service and Streaming.

### Web Service

Deploying a Flask app on an EC2 instance allows the system to receive user requests through an endpoint and send responses back via a frontend. This method has been developed locally but has not yet been deployed. It remains a potential future option.

- **Deploy Locally:**
  - To deploy the Flask app locally:
    ```bash
    make run_flask
    ```
  - To deploy the Flask app locally with MLFlow experiment tracking:
    ```bash
    make run_flask_with_mlflow
    ```
  - To test the Flask app locally:
    ```bash
    make run_web_test
    ```

### Streaming

The final deployment of the project leverages a serverless event-driven architecture using AWS Kinesis to handle user events and provide responses.

I have chosen this method for its scalability and efficiency. The deployment code's Lambda function is dockerized to ensure seamless cloud deployment. You can find the Dockerfile [here](deployment/streaming/Dockerfile), which includes all necessary utility dependencies.

The streaming approach is run and tested in:

- **Locally**: [Integration tests](#integration-tests).
- **Production**: [terraform](#infrastructure-and-automation-terraform-infrastructure-as-code) and [CI/CD Pipeline](#cicd-pipeline)

### Common Elements

In both the Web Service and Streaming methods, the scaler and model are retrieved from the model registry developed during the research phase and uploaded to S3. This can be achieved using MLFlow or Boto3, avoiding the need to upload the database to load the artifacts.

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

To complete this project, the CI/CD pipeline integrates the [infrastructure](#infrastructure-and-automation-terraform-infrastructure-as-code) and [good practices](#good-practices) sections, streamlining the deployment of new features.

This pipeline is designed for a typical workflow where direct pushes to the main branch are not allowed. While it assumes direct pushes to the develop branch are possible, it is generally better to push to a feature branch first and then create a pull request to develop.

The pipeline consists of two parts:

- **CI Pipeline**: Runs on pushes to the develop branch to ensure everything is functioning correctly.
- **CD Pipeline**: Runs on pull requests to the main branch and deploys changes directly.
Both pipelines are triggered only if files affecting any phase of the pipeline are changed or created. This is managed by specifying paths that need monitoring.

CI/CD pipelines work together, as a reliable CI pipeline is essential for confidently deploying changes to production.

### CI Pipeline
The CI pipeline ensures the system operates correctly when new features are added. It tests all code through unit and integration tests, and verifies the Terraform infrastructure by running terraform plan with production variables and the production backend state.

This pipeline is triggered by pull requests to the main branch or pushes to the develop branch, as these actions are critical for monitoring in this workflow.

To view the code, see the [CI pipeline configuration](.github/workflows/ci-tests.yml).

### CD Pipeline
The CD pipeline enables seamless integration of new changes into the production system. It runs the terraform apply steps in production, saves the Lambda image in the ECR, and updates the Lambda function.

This pipeline is triggered only when a pull request to the main branch is accepted, as this is the appropriate moment to deploy the previously implemented changes to production.

To view the code, see the [CD pipeline configuration](.github/workflows/cd-deploy.yml).

### How to Use

The pipelines are triggered automatically based on the actions mentioned above. Before utilizing the pipelines, please follow these steps:

1. **Add AWS Credentials**:
   - In the repository's secrets configuration section, add `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.

2. **Test Workflows without Pull Requests**:
   - If you want to test the workflows without making pull requests, temporarily modify the configuration file as follows:

    ```yaml
    on:
      push:
        branches:
          - 'main'  # Replace with the name of your branch
    ```

This modification allows the workflows to be triggered on pushes to the specified branch, facilitating easier testing.

## Future steps
- Migrate Training Pipeline to cloud
- Deployment of the web service
- Added to the firts event streaming the web service
- Automatize the training when the data drifs surpasses a treshold, instead of only alert
- Deploy the monitoring module
- Finish dynamic data ingestion in the monitoring module
- Finish complete integration between dashboard monitoring and alerts
