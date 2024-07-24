from functools import partial

import mlflow
import pandas as pd
import scipy.stats as stats
from hyperopt import STATUS_OK, Trials, fmin, hp, space_eval, tpe
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

if "transformer" not in globals():
    from mage_ai.data_preparation.decorators import transformer
if "test" not in globals():
    from mage_ai.data_preparation.decorators import test


def init_mlflow():
    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("student-performance")


def objective(params, X_train, X_val, y_train, y_val):
    with mlflow.start_run(nested=True):
        print(params)
        classifier_type = params["type"]
        mlflow.set_tag("model", classifier_type)
        del params["type"]
        if classifier_type == "svm":
            clf = SVC(**params)
        elif classifier_type == "rf":
            clf = RandomForestClassifier(**params)
        elif classifier_type == "dt":
            clf = DecisionTreeClassifier(**params)
        elif classifier_type == "xgb":
            clf = XGBClassifier(**params)
        else:
            return 0
        mlflow.log_params(params)

        clf.fit(X_train, y_train)

        y_pred = clf.predict(X_val)
        accuracy = accuracy_score(y_val, y_pred)
        mlflow.log_metric("accuracy", accuracy)
        f1 = f1_score(y_val, y_pred, average="macro")
        mlflow.log_metric("f1_score", f1)

        if getattr(clf, "predict_proba", None):
            y_pred_proba = clf.predict_proba(X_val)
            roc_auc = roc_auc_score(
                y_val, y_pred_proba, average="micro", multi_class="ovr"
            )
            mlflow.log_metric("roc_auc", roc_auc)

        mlflow.sklearn.log_model(sk_model=clf, artifact_path="mlruns")
        mlflow.log_artifact(
            local_path="minmax_scaler.bin", artifact_path="minmax_scaler"
        )

    return {"loss": -f1, "status": STATUS_OK}


def hyperopt_training(X_train, X_val, y_train, y_val):

    search_space = hp.choice(
        "classifier_type",
        [
            {"type": "svm", "C": hp.lognormal("SVM_C", 0, 1.0)},
            {
                "type": "rf",
                "max_depth": hp.randint("rf_max_depth", 5, 100),
                "criterion": hp.choice("rf_criterion", ["gini", "entropy"]),
            },
            {
                "type": "dt",
                "criterion": hp.choice("dt_criterion", ["gini", "entropy"]),
                "splitter": hp.choice("dt_splitter", ["best", "random"]),
                "class_weight": hp.choice("dt_class_weight", ["balanced", None]),
            },
            {
                "type": "xgb",
                "learning_rate": hp.choice(
                    "xgb_learning_rate", [0.0005, 0.001, 0.01, 0.5, 1]
                ),
                "max_depth": hp.choice("xgb_max_depth", range(3, 21, 3)),
                "gamma": hp.choice("xgb_gamma", [i / 10.0 for i in range(0, 5)]),
                "colsample_bytree": hp.choice(
                    "xgb_colsample_bytree", [i / 10.0 for i in range(3, 10)]
                ),
                "reg_alpha": hp.choice("xgb_reg_alpha", [1e-5, 1e-2, 0.1, 1, 10, 100]),
                "reg_lambda": hp.choice(
                    "xgb_reg_lambda", [1e-5, 1e-2, 0.1, 1, 10, 100]
                ),
                "seed": hp.choice("xgb_seed", [0, 7, 42]),
            },
        ],
    )

    algo = tpe.suggest
    objective_with_data = partial(
        objective, X_train=X_train, X_val=X_val, y_train=y_train, y_val=y_val
    )

    with mlflow.start_run(nested=True):
        best_result = fmin(
            fn=objective_with_data,
            space=search_space,
            algo=algo,
            max_evals=32,
            trials=Trials(),
        )
    print(space_eval(search_space, best_result))


@transformer
def transform(data, *args, **kwargs):
    data = [pd.DataFrame(ind_data) for ind_data in data["transformations"][0]]

    X_train, X_val, X_test, y_train, y_val, y_test = data

    init_mlflow()
    hyperopt_training(X_train, X_val, y_train, y_val)

    return True


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, "The output is undefined"
