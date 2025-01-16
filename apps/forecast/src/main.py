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
from build import build_model

from models import tune_base_models
from sklearn.ensemble import StackingRegressor
import joblib
import json

from feats.skill import SkillFeature
from feats.time_factor import time_factor
from train_data import gen_train_data, prepare_data, labelers
from utils import fetch_match_history, fetch_fixtures, fetch_teams, handle_team_points

async def fetch(session: aiohttp.ClientSession, endpoint):
    async with session.get(f"http://127.0.0.1:5000{endpoint}") as response:
        return await response.json()

    return matches

def compute_model(model, X_train, y_train):
    model.fit(X_train, y_train)

    return model


async def main():
    matches, stats = await fetch_match_history()
    # teams = await fetch_teams()

    # l = labelers(teams)

    # stats, features = prepare_data(matches.copy(), stats.copy(), l)
    # X, y = gen_train_data(stats, features)

    # train_data = X.copy()
    # train_data["created_xg"] = y

    # train_data.to_csv("train_data.csv", index=False)
    # print(X.iloc[0])
    model:StackingRegressor = joblib.load("stack_model_2025-01-15 22:01:56.443118.pkl")

    l = joblib.load("labelers.pkl")
    features = joblib.load("features.pkl")


    # models = train_model(X, y, 34)

    fmatches = []
    fixtures = await fetch_fixtures()
    fixtures = fixtures.sort_values("round")
    for _,f in fixtures.iterrows():
        if f["round"] == 23:
            break
        m = predict_fixture(f, stats, model, features, l["team"], matches)
        fmatches.append(m)

    with open("matches.json", "w") as f:
        f.write(json.dumps(fmatches))

def predict_fixture(fixture, stats, model, features, team_labeler: LabelEncoder, matches) -> dict:
    sf = match_strategy_predict(stats, fixture, features.values())
    fixture = time_factor(fixture)

    home_point = handle_team_points(fixture["home_team"], matches)
    print("home", home_point)
    away_point = handle_team_points(fixture["away_team"], matches)
    print("home", away_point)

    team_label = team_labeler.transform([fixture["home_team"], fixture["away_team"]])

    # Create prediction DataFrame with explicit types
    X_pred = pd.DataFrame({
        "team_label": [team_label[0], team_label[1]],
        "mif": [0.3, 0.3],
        "fatigue": [0.0, 0.0],
        "hours": [int(fixture["hours"]), int(fixture["hours"])],
        "weekdays": [int(fixture["weekdays"]), int(fixture["weekdays"])],
        "points": [home_point, away_point],
    })

    for f in features.values():
        X_pred[f"{f.name}_cluster"] = sf[f"{f.name}_cluster"]

        X_pred[f"{f.name}scores_xg_ratio"] = f.results["scores_xg_ratio"]
        X_pred[f"{f.name}mean_xg"] = f.results["mean_xg"]
        X_pred[f"{f.name}mean_goals"] = f.results["mean_goals"]

    print(X_pred.iloc[0])
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

def predict(
    X: pd.DataFrame,
    models: tuple[RandomForestRegressor, GradientBoostingRegressor, LGBMRegressor],
    weights,
) -> np.ndarray:
    pred = [model.predict(X) for model in models]
    return sum([w * p for w, p in zip(weights, pred)])


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
        m = match_data
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
