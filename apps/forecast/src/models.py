from utils import handle_points
from feats.mif import create_mif_model

def prepare_models():
    # MIF model
    matches = handle_points(matches)

    mif_data = matches[
        ["home_team", "away_team", "home_points", "away_points", "attendances"]
    ].copy()

    mif_model = create_mif_model(mif_data)


    return mif_model
