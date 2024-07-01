import pandas as pd
import mlflow
import pickle
from sklearn.preprocessing import MinMaxScaler


if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(data, *args, **kwargs):
    
    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("student-performance")

    df_data = [pd.DataFrame(ind_data) for ind_data in data]

    X_train, X_val, X_test, y_train, y_val, y_test = df_data
    

    minmax_cols = ['ParentalEducation', 'StudyTimeWeekly',
                   'Absences', 'ParentalSupport']
    sc = MinMaxScaler()

    x_sc_train = sc.fit_transform(X_train.loc[:, minmax_cols])
    X_train.loc[:, minmax_cols] = x_sc_train

    with open('minmax_scaler.bin', 'wb') as f_out:
        pickle.dump(sc, f_out)
    
    mlflow.log_artifact(local_path="minmax_scaler.bin", artifact_path="minmax_scaler")

    x_sc_val = sc.transform(X_val.loc[:, minmax_cols])
    X_val.loc[:, minmax_cols] = x_sc_val

    x_sc_test = sc.transform(X_test.loc[:, minmax_cols])
    X_test.loc[:, minmax_cols] = x_sc_test

    return X_train, X_val, X_test, y_train, y_val, y_test


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
