include .env


# Define a default target
.PHONY: all
all: run_mlflow run_flask run_tests

.PHONY: setup_web
setup_web: run_mlflow run_flask

# Target to run the MLflow server
.PHONY: run_mlflow
run_mlflow:
	@echo "Starting MLflow server..."
	call .venv/Scripts/activate && start /B mlflow server -h ${MLFLOW_HOST} -p ${MLFLOW_PORT} --backend-store-uri ${MLFLOW_BACKEND_URI} --default-artifact-root ${MLFLOW_ARTIFACT_URI} &

# Target to run the Flask app
.PHONY: run_flask
run_flask:
	@echo "Starting Flask app..."
	call .venv/Scripts/activate && start /B python ./deployment/web_service/predict.py > flask.log 2>&1

run_flask_with_mlflow:
	@$(MAKE) run_mlflow
	ping -n 10 127.0.0.1 > NUL
	@$(MAKE) run_flask

.PHONY: run_web_test
run_web_test: 
	@echo "Running tests with MLFLOW_TRACKING_URI set to an empty string..."
	call .venv/Scripts/activate && set MLFLOW_TRACKING_URI= && start /B python ./deployment/web_service/predict.py > flask.log 2>&1
	ping -n 10 127.0.0.1 > NUL
	call .venv/Scripts/activate&& set MLFLOW_TRACKING_URI= && python ./deployment/web_service/test.py
	@$(MAKE) clean

# Clean up background jobs (if needed)
.PHONY: clean
clean:
	@echo "Cleaning up background processes..."
	@taskkill /F /IM "mlflow.exe" || (echo "No mlflow.exe process found, continuing..." && exit 0)
	@taskkill /F /IM "python.exe" || (echo "No python.exe process found, continuing..." && exit 0)
