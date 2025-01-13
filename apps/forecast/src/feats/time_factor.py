import pandas as pd
from datetime import datetime

def time_factor(data: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    d = data.copy()

    # Handle both DataFrame and Series inputs
    if isinstance(d, pd.Series):
        played_at = pd.to_datetime(d["played_at"]*1000)
        d["hours"] = played_at.hour + 1
        d["weekdays"] = played_at.dayofweek + 1
    else:
        d["played_at"] = pd.to_datetime(d["played_at"]*1000)
        d["hours"] = d["played_at"].dt.hour.add(1)
        d["weekdays"] = d["played_at"].dt.dayofweek.add(1)

    return d
