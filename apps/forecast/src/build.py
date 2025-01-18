from utils import fetch_match_history, fetch_teams
from train_data import gen_train_data, prepare_data, labelers
from prediction_data import team_strategy_predict
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import json

import os
import pandas as pd
import joblib
import asyncio

from models import (
    create_base_models,
    opt_base_models,
    create_stack_model,
    test_cv_model,
)

from bases import (
    DEFAULT_TRAIN_DATA_FILE,
    SKIP_OPTIMIZE,
    pathify,
    
    TRAIN_DATA,
    MODEL_FILE,
    FEATURES_FILE,
    LABELERS_FILE,
    TEAM_STRATEGY_FILE,
    TEST_RESULTS_FILE,
)

async def extract_data():
    matches, stats = await fetch_match_history()
    teams = await fetch_teams()

    l = labelers(teams)

    stats, features = prepare_data(matches.copy(), stats.copy(), l)

    joblib.dump(l, LABELERS_FILE)
    joblib.dump(features, FEATURES_FILE)

    X, y = gen_train_data(stats, features)

    train_data = X.copy()
    train_data["created_xg"] = y

    predicts = {}
    for _, t in teams.iterrows():
        predicts[t["id"]] = team_strategy_predict(
            l["team"].transform([t["id"]])[0], X, features
        )

    json.dump(predicts, open(TEAM_STRATEGY_FILE, "w"))

    train_data.to_csv(TRAIN_DATA, index=False)

async def build_model():
    # extract data from the scraper_db to build the model
    os.makedirs(pathify("."), exist_ok=True)

    data: pd.DataFrame = None
    if os.path.exists(DEFAULT_TRAIN_DATA_FILE):
        with open(DEFAULT_TRAIN_DATA_FILE, "r") as f:
            data = pd.read_csv(f)
    else:
        await extract_data()
        with open(TRAIN_DATA, "r") as f:
            data = pd.read_csv(f)

    # train the model
    models = create_base_models()

    X_train, X_test, y_train, y_test = train_test_split(
        data.copy().drop("created_xg", axis=1),
        data["created_xg"].ravel(),
        test_size=0.2,
    )

    test_results = {}

    if not SKIP_OPTIMIZE:
        opt_res = opt_base_models(
            models,
            X_train,
            y_train,
        )
        test_results["base_models"] = opt_res

    stack_model = create_stack_model(models)

    score = test_cv_model(stack_model, X_train, y_train)
    test_results["cv_score"] = score

    stack_model.fit(X_train, y_train)

    y_pred = stack_model.predict(X_test)
    test_results["rmse"] = mean_squared_error(y_test, y_pred)
    print(test_results)

    # export models to the models directory
    json.dump(test_results, open(TEST_RESULTS_FILE, "w"))
    joblib.dump(stack_model, MODEL_FILE)


async def main():
    print('Forecast app is running...')

    await build_model()

if __name__ == '__main__':
    print('Building forecast app...')
    # Build the forecast app here
    asyncio.run(main())
    print('Forecast ml built successfully!')
