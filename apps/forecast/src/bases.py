import datetime
import os

SKIP_OPTIMIZE = os.getenv("FORECAST_SKIP_OPTIMIZE", True)
MODEL_PATH = os.getenv("FORECAST_MODEL_PATH", "../.models/")
MODEL_TAG = os.getenv("FORECAST_MODEL_TAG", f"model_{datetime.datetime.now()}")

def pathify(path):
    return os.path.join(MODEL_PATH, MODEL_TAG, path)

DEFAULT_TRAIN_DATA_FILE = os.getenv("DEFAULT_TRAIN_DATA_FILE", pathify("../../train_data.csv"))

# files to export
TRAIN_DATA = pathify("train_data.csv")
MODEL_FILE = pathify("model")
FEATURES_FILE = pathify("features")
LABELERS_FILE = pathify("labelers")
TEAM_STRATEGY_FILE = pathify("team_strategy.json")
TEST_RESULTS_FILE = pathify("results.json")
