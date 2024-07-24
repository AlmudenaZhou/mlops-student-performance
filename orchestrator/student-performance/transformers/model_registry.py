import mlflow
from mlflow.entities import ViewType
from mlflow.store.artifact.runs_artifact_repo import RunsArtifactRepository
from mlflow.tracking import MlflowClient

if "transformer" not in globals():
    from mage_ai.data_preparation.decorators import transformer
if "test" not in globals():
    from mage_ai.data_preparation.decorators import test


def register_model():
    client = MlflowClient(tracking_uri="http://mlflow:5000")
    experiment_name = "student-performance"

    experiment_id = [
        experiment.experiment_id
        for experiment in client.search_experiments()
        if experiment.name == experiment_name
    ]

    run = client.search_runs(
        experiment_ids=experiment_id,
        run_view_type=ViewType.ACTIVE_ONLY,
        order_by=["metrics.accuracy DESC"],
    )[0]

    run_id = run.info.run_id

    mlflow.register_model(model_uri=f"runs:/{run_id}/models", name=experiment_name)

    model_uri = f"runs:/{run_id}/model"

    model_src = RunsArtifactRepository.get_underlying_uri(model_uri)
    filter_string = "run_id='{}'".format(run_id)
    results = client.search_model_versions(filter_string)
    model_version = results[0].version

    new_stage = "Production"
    client.transition_model_version_stage(
        name=experiment_name,
        version=model_version,
        stage=new_stage,
        archive_existing_versions=False,
    )


@transformer
def transform(data, *args, **kwargs):
    register_model()
