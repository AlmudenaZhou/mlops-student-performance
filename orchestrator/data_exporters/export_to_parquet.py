import pandas as pd

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data_to_parquet(data, **kwargs) -> None:
    names = ['x_train', 'x_val', 'x_test', 'y_train', 'y_val', 'y_test']

    for ind_data, name in zip(data, names):
        ind_data = pd.DataFrame(ind_data)
        ind_data.to_parquet(f'data/{name}.parquet')
        
