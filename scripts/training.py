import pandas as pd
from sklearn.model_selection import train_test_split

from scripts.read_write import ReadWriteParquet

data = pd.read_csv("data/Student_performance_data.csv")
data.head()


def split_data(data, output_folder):
    X = data.drop(["GPA", "GradeClass"], axis=1)
    y = data[["GradeClass"]]

    X_train, X_val_test, y_train, y_val_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    X_val, X_test, y_val, y_test = train_test_split(
        X_val_test, y_val_test, test_size=0.5, random_state=42, stratify=y_val_test
    )

    rwp = ReadWriteParquet()
    rwp
