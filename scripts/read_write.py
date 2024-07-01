import os 
import pandas as pd


class ReadWriteParquet:
    def __init__(self) -> None:
        self.endpoint_url = os.getenv('S3_ENDPOINT_URL', None)

        self.options = {
                'client_kwargs': {
                    'endpoint_url': self.endpoint_url
                }
            }
        
    def read_data(self, filename):

        if self.endpoint_url:
            df = pd.read_parquet(filename, storage_options=self.options)
        else:
            df = pd.read_parquet(filename)

        return df

    def save_data(self, df, filename):
        if self.endpoint_url:
            df.to_parquet(
                filename,
                engine='pyarrow',
                compression=None,
                index=False,
                storage_options=self.options
            )
        else:
            df.to_parquet(filename, engine='pyarrow', index=False)