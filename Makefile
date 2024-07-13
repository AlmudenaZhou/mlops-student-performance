# Define a default target
.PHONY: all
all: run_mlflow run_flask run_tests

.PHONY: setup_web
setup_web: run_mlflow run_flask

# Target to run the MLflow server
.PHONY: run_mlflow
run_mlflow:
	@echo "Starting MLflow server..."
	call .venv/Scripts/activate && start /B mlflow server -h 127.0.0.1 -p 5000 --backend-store-uri sqlite:///mlflow_db/mlflow.db --default-artifact-root s3://mlflow-artifact-student-performance &
	
	ping -n 10 127.0.0.1 > NUL

# Target to run the Flask app
.PHONY: run_flask
run_flask:
	@echo "Starting Flask app..."
	call .venv/Scripts/activate && start /B python ./deployment/web_service/predict.py > flask.log 2>&1
	
	ping -n 10 127.0.0.1 > NUL

# Target to run the tests
.PHONY: run_tests
run_tests:
	@echo "Running tests..."
	call .venv/Scripts/activate && python ./deployment/web_service/test.py

# Clean up background jobs (if needed)
.PHONY: clean
clean:
	@echo "Cleaning up background processes..."
	taskkill /F /IM "mlflow.exe" || true
	taskkill /F /IM "python.exe" || true
