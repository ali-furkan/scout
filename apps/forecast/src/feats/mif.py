import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor

def mif_series(data: pd.DataFrame):
    d = data["attendances"].copy()
    mean_attendance = d.mean(numeric_only=True)
    d = d.fillna(mean_attendance)
    d = d.apply(lambda x: mean_attendance if x < 1000 else x)

    s = StandardScaler()
    impact_f = s.fit_transform(d.values.reshape(-1, 1))

    return impact_f

# Prediction model
def create_mif_model(data: pd.DataFrame) -> RandomForestRegressor:
    d = data[["home_team","away_team","home_points","away_points","attendances"]].copy()

    # Encode categorical variables
    le = LabelEncoder()
    d["home_team_encoded"] = le.fit_transform(d["home_team"])
    d["away_team_encoded"] = le.fit_transform(d["away_team"])

    # Prepare features for model
    X = np.column_stack([
        d["home_team_encoded"],
        d["away_team_encoded"],
        d["home_points"],
        d["away_points"]
    ])

    model = RandomForestRegressor()
    model.fit(X, mif_series(d))

    return model
