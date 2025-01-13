import aiohttp
import asyncio
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from lightgbm import LGBMRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from scipy.stats import poisson
import matplotlib.pyplot as plt
import seaborn as sns
import json

from feats.skill import SkillFeature
from feats.time_factor import time_factor
from utils import prepare

async def fetch(session: aiohttp.ClientSession, endpoint):
    async with session.get(f"http://127.0.0.1:5000{endpoint}") as response:
        return await response.json()

    return matches

def compute_model(model, X_train, y_train):
    model.fit(X_train, y_train)

    return model

def compute_test(name, model, X_train, X_test, y_train, y_test):
    from sklearn.metrics import mean_squared_error

    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    print(name, mean_squared_error(y_test, pred))
    return pred


async def main():
    matches = None
    fixtures = None
    stats = None

    async with aiohttp.ClientSession() as session:
        data_matches = await fetch(session,"/matches/results?limit=400")
        data_fixtures = await fetch(session,"/matches/fixtures?limit=400")
        data_stats = await fetch(session, "/stats/teams?limit=400")

        matches = pd.DataFrame(data_matches["matches"])
        fixtures = pd.DataFrame(data_fixtures["matches"])
        stats = pd.DataFrame(data_stats["stats"])

    stats, mif_model, features = prepare(matches.copy(), stats.copy())

    # trainning model
    X = pd.DataFrame({
        "mif": stats["impact"],
        "fatigue": stats["fatigue"],
        "hours": stats["hours"],
        "weekdays": stats["weekdays"],
    })

    l = LabelEncoder()
    X["mif"] = l.fit_transform(X["mif"])
    X["fatigue"] = l.fit_transform(X["fatigue"])
    X["hours"] = l.fit_transform(X["hours"])
    X["weekdays"] = l.fit_transform(X["weekdays"])

    for f in features.values():
        X[f"{f.name}_cluster"] = stats[f"{f.name}_cluster"]
        X[f"{f.name}_cluster"] = X[f"{f.name}_cluster"].astype("category")
        X[f"{f.name}_cluster"] = LabelEncoder().fit_transform(X[f"{f.name}_cluster"])

        X[f"{f.name}scores_xg_ratio"] = f.results["scores_xg_ratio"]
        X[f"{f.name}mean_xg"] = f.results["mean_xg"]
        X[f"{f.name}mean_goals"] = f.results["mean_goals"]

    y = stats["created_xg"]

    a,b,weights = run_test_model(X, y, 34)

    models = train_model(X, y, 34)

    matches = []
    fixtures = fixtures.sort_values("round")
    for _,f in fixtures.iterrows():
        if f["round"] == 23:
            break
        m = predict_fixture(f, stats, models, weights, features)
        matches.append(m)

    with open("matches.json", "w") as f:
        f.write(json.dumps(matches))
        json.dumps(matches)


def predict_fixture(fixture, stats, models, model_weights, features) -> dict:
    sf = match_strategy_predict(stats, fixture, features.values())
    fixture = time_factor(fixture)

    # Convert hours and weekdays to numeric values
    X_pred = pd.DataFrame({
        "mif": [0.3, 0.3],
        "fatigue": [0.0, 0.0],
        "hours": [int(fixture["hours"]), int(fixture["hours"])],  # Convert to int
        "weekdays": [int(fixture["weekdays"]), int(fixture["weekdays"])],  # Convert to int
    })

    for f in features.values():
        X_pred[f"{f.name}_cluster"] = sf[f"{f.name}_cluster"]
        X_pred[f"{f.name}_cluster"] = LabelEncoder().fit_transform(X_pred[f"{f.name}_cluster"])

        X_pred[f"{f.name}scores_xg_ratio"] = f.results["scores_xg_ratio"]
        X_pred[f"{f.name}mean_xg"] = f.results["mean_xg"]
        X_pred[f"{f.name}mean_goals"] = f.results["mean_goals"]

    # Ensure all columns are numeric
    X_pred = X_pred.astype(float)

    pred = predict(X_pred, models, model_weights)

    lambda_home = pred[0]
    lambda_away = pred[1]

    max_goals = 8

    home_goal_probs = [poisson.pmf(k, lambda_home) for k in range(max_goals)]
    away_goal_probs = [poisson.pmf(k, lambda_away) for k in range(max_goals)]

    draw_probs = sum(home_goal_probs[k] * away_goal_probs[k] for k in range(max_goals))

    home_win_prob = sum(
        home_goal_probs[i] * sum(away_goal_probs[j] for j in range(i))
        for i in range(1, max_goals)
    )
    away_win_prob = sum(
        away_goal_probs[i] * sum(home_goal_probs[j] for j in range(i))
        for i in range(1, max_goals)
    )

    match = {}
    match["id"] = fixture["id"]
    match["home_win_prob"] = home_win_prob
    match["away_win_prob"] = away_win_prob
    match["home_goals_probs"] = home_goal_probs
    match["away_goals_probs"] = away_goal_probs
    match["draw_prob"] = draw_probs

    m = []
    for i in range(max_goals):
        row = []
        for j in range(max_goals):
            row.append(home_goal_probs[i] * away_goal_probs[j])
        m.append(row)

    match["heatmap"] = m

    return match

def train_model(X,y,num) -> tuple[RandomForestRegressor, GradientBoostingRegressor, LGBMRegressor]:
    a = compute_model(
        RandomForestRegressor(random_state=num, n_estimators=300, max_depth=32), X, y
    )
    b = compute_model(GradientBoostingRegressor(random_state=num), X, y)
    c = compute_model(LGBMRegressor(random_state=num), X, y)

    # Fix: Create actual tuple instead of tuple type hint
    return (a, b, c)

def predict(
    X: pd.DataFrame,
    models: tuple[RandomForestRegressor, GradientBoostingRegressor, LGBMRegressor],
    weights,
) -> np.ndarray:
    # Remove unnecessary list conversion since models is already iterable
    pred = [model.predict(X) for model in models]
    return sum([w * p for w, p in zip(weights, pred)])


def run_test_model(X,y,r_num) -> tuple[list, list, list]:

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    lgbm0 = LGBMRegressor(random_state=r_num)
    a = compute_test("LGBM-cat", lgbm0, X_train, X_test, y_train, y_test)

    rfr0 = RandomForestRegressor(random_state=r_num, n_estimators=300, max_depth=32)
    b = compute_test("RFR-cat", rfr0, X_train, X_test, y_train, y_test)

    gbr = GradientBoostingRegressor(random_state=r_num)
    c = compute_test("GBR", gbr, X_train, X_test, y_train, y_test)

    models = [a,b,c]
    w = [mean_squared_error(y_test, pred) for pred in models]
    inverse_rmse = [1 / rmse for rmse in w]
    weights = [inv / sum(inverse_rmse) for inv in inverse_rmse]

    return sum([w * pred for w, pred in zip(weights, models)]), y_test, weights


def match_strategy_predict(
    stats: pd.DataFrame, match_data: pd.DataFrame, feats: list[SkillFeature]
) -> pd.DataFrame:
    home_team = stats.loc[stats["team"] == match_data["home_team"]]
    away_team = stats.loc[stats["team"] == match_data["away_team"]]

    # Initialize result DataFrame with proper index
    res = pd.DataFrame(index=range(2))  # 2 rows for home and away teams
    
    for i, t in enumerate([home_team, away_team]):
        # Fill NaN values with mean for numerical columns
        t = t.fillna(t.mean(numeric_only=True))
        t_mean = t.mean(numeric_only=True)
        t_top_5_mean = t.nlargest(5, 'played_at').mean(numeric_only=True)
        t_predict = t_mean * 0.5 + t_top_5_mean * 0.5

        for f in feats:
            feature_data = t_predict[f.cols].fillna(t_predict[f.cols].mean())
            predicted_cat = f.predict(pd.DataFrame([feature_data]))
            # Convert prediction to scalar value before assignment
            res.at[i, f"{f.name}_cluster"] = predicted_cat[0]

    return res


if __name__ == '__main__':
    asyncio.run(main())
