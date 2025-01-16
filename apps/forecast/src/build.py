from utils import fetch_match_history, fetch_teams
from train_data import gen_train_data, prepare_data, labelers
from prediction_data import prepare_fixture, team_strategy_predict
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import json

import os
import pandas as pd
import joblib
import datetime
import asyncio

from models import (
    create_base_models,
    tune_base_models,
    create_stack_model,
    test_cv_model,
)

SKIP_TUNNING = os.getenv("SKIP_TUNNING", True)
EXPORT_MODEL_PATH = os.getenv("MODEL_PATH", f"stack_model_{datetime.datetime.now()}.pkl")

async def extract_data(file = "train_data.csv"):

    matches, stats = await fetch_match_history()
    teams = await fetch_teams()

    l = labelers(teams)

    stats, features = prepare_data(matches.copy(), stats.copy(), l)

    joblib.dump(l, "labelers.pkl")
    joblib.dump(features, "features.pkl")

    X, y = gen_train_data(stats, features)

    train_data = X.copy()
    train_data["created_xg"] = y

    predicts = {}
    for _, t in teams.iterrows():
        predicts[t["id"]] = team_strategy_predict(
            l["team"].transform([t["id"]])[0], X, features
        )

    json.dump(predicts, open("teams_strategy_predicts.json", "w"))

    train_data.to_csv(file, index=False)

async def build_model():
    # extract data from the scraper_db to build the model
    data: pd.DataFrame = None
    if not os.path.exists("train_data.csv"):
        await extract_data()

    with open("train_data.csv", "r") as f:
        data = pd.read_csv(f)
    # train the model
    models = create_base_models()

    X_train, X_test, y_train, y_test = train_test_split(
        data.copy().drop("created_xg", axis=1), 
        data['created_xg'].ravel(), 
        test_size=0.2, 
        random_state=42
    )

    tune_opt_res: dict = None
    if not SKIP_TUNNING:
        tune_opt_res = tune_base_models(
            models,
            X_train,
            y_train,
            34,
        )
    stack_model = create_stack_model(models)

    score = test_cv_model(stack_model, X_train, y_train)

    stack_model.fit(X_train, y_train)

    y_pred = stack_model.predict(X_test)
    print(f"CV Train Score: {score}")
    print(f"Test Score: {mean_squared_error(y_test, y_pred)}")

    # export models to the models directory
    joblib.dump(stack_model, EXPORT_MODEL_PATH)


async def main():
    print('Forecast app is running...')

    await build_model()

if __name__ == '__main__':
    print('Building forecast app...')
    # Build the forecast app here
    asyncio.run(main())
    print('Forecast ml built successfully!')
