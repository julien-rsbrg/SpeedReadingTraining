import os
import pandas as pd

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


def save_performance(exercise_name, row):
    os.makedirs(_DATA_DIR, exist_ok=True)
    path = os.path.join(_DATA_DIR, f"{exercise_name}.csv")
    df_new = pd.DataFrame([row])
    if os.path.exists(path):
        df_new.to_csv(path, mode="a", header=False, index=False)
    else:
        df_new.to_csv(path, index=False)


def load_performance(exercise_name):
    path = os.path.join(_DATA_DIR, f"{exercise_name}.csv")
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)
