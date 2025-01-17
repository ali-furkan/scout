from flask import Flask, request, Response
from sklearn.ensemble import StackingRegressor
from feats.skill import SkillFeature
from utils import handle_fixture
import os
import joblib
import json

import pandas as pd

MODEL_PATH = os.environ.get("MODEL_PATH", "model.pkl")
FEATURE_PATH = os.environ.get("FEATURE_PATH", "features.pkl")
STRATEGY_PATH = os.environ.get("STRATEGY_PATH", "teams_strategy_predicts.json")

app = Flask(__name__)

@app.post("/stats/predict")
def predict():
    request_data = json.loads(request.get_data())

    params = request_data["params"]
    X_pred = pd.json_normalize(params)

    print("params length", X_pred.keys())

    prediction = app.model.predict(X_pred).tolist()
    return {"prediction": prediction}

@app.post("/fixture/predict")
def predict_fixture():
    data = request.get_json()
    home = data["home"]
    away = data["away"]

    return {"fixture": handle_fixture(home, away)}

@app.get("/team-strategy")
def get_teams_strategy():
    return {
        "teams": app.strategy
    }

@app.get("/team-strategy/<team_id>")
def get_team_strategy(team_id):
    return {
        "team": app.strategy.get(team_id, {})
    }

@app.get("/model")
def get_model():
    m: StackingRegressor = app.model

    fi = []

    for e in m.estimators_:
        fi.append(e.feature_importances_.tolist())

    ffi = m.final_estimator_.feature_importances_.tolist()

    return {
        "model": {
            "name": MODEL_PATH,
            "type": type(m).__name__,
            "base_models": [type(e).__name__ for e in m.estimators_],
            "final_model": type(m.final_estimator_).__name__,
            "features_names":  m.feature_names_in_.tolist(),
            "features_importances": {
                "estimators": fi,
                "final_estimator": ffi
            }
        }
    }

@app.get("/features")
def get_features():
    features: dict[SkillFeature] = app.features

    fd = {}
    for f in features.values():
        f: SkillFeature
        fd[f.name] = {
            "name": f.name,
            "n_clusters": 5,
            "clusters": [],
            "cluster_centers": f.model.cluster_centers_.tolist()
        }
        for i in range(5):
            instance = f.results.loc[f.results[f.cluster_field] == i].iloc[0]
            fd[f.name]["clusters"].append({
                "cat": i,
                "scores_xg_ratio": instance["scores_xg_ratio"],
                "mean_xg": instance["mean_xg"],
                "mean_goals": instance["mean_goals"]
            })

    return Response(json.dumps({
        "features": fd
    }, sort_keys=False), mimetype="application/json")

def init_app(a):
    a.model = joblib.load(MODEL_PATH)
    a.features = joblib.load(FEATURE_PATH)
    with open(STRATEGY_PATH, "r") as f:
        a.strategy = json.load(f)

if __name__ == "__main__":
    init_app(app)
    app.run(debug=True, host="0.0.0.0", port=5001)
