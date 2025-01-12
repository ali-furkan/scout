import pandas as pd
from datetime import datetime

def time_factor(data: pd.DataFrame) -> pd.DataFrame:
    d = data.copy()

    d["played_at"] = pd.to_datetime(d["played_at"]*1000).copy()

    d["hours"] = d["played_at"].dt.hour.add(1).astype(str).astype("category")
    d["weekdays"] = d["played_at"].dt.dayofweek.add(1).astype(str).astype("category")

    return d
