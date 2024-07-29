import pandas as pd
from datetime import datetime, timedelta
import os
import uuid


def process_parquet_files(data_folder):
    # Get current date and time
    current_time = datetime.now().replace(second=0, microsecond=0)

    # List of file pairs to process
    file_pairs = [
        ('x_train.parquet', 'y_train.parquet'),
        ('x_val.parquet', 'y_val.parquet'),
        ('x_test.parquet', 'y_test.parquet'),
    ]

    last_ts = current_time

    for (x_file, y_file) in file_pairs:

        x_df = pd.read_parquet(os.path.join(data_folder, x_file))
        y_df = pd.read_parquet(os.path.join(data_folder, y_file))
        num_records = len(x_df)

        df = pd.concat([x_df, y_df], axis=1)
        print(num_records)

        timestamps = pd.date_range(end=last_ts, periods=num_records, freq='1min')

        # Add Timestamp column
        df['Timestamp'] = timestamps

        uuid_values = [uuid.uuid4() for _ in range(len(x_df))]
        df['uuid'] = uuid_values
        df['uuid'] = df['uuid'].astype("string")

        # Save processed files
        filename = x_file.replace("x_", "")
        os.makedirs(os.path.join(data_folder, 'features'), exist_ok=True)
        df.to_parquet(
            os.path.join(data_folder, 'features', f'processed_{filename}'), index=False
        )

        last_ts = timestamps[0] - timedelta(minutes=1)

    print("Processing complete. Check the 'data' folder for processed files.")


if __name__ == '__main__':
    data_folder = 'data'
    process_parquet_files(data_folder)
