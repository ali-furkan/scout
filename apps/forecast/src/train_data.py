import os
import asyncio
import aiohttp

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from feats.skill import SkillFeature, get_xg_features
from feats.time_factor import time_factor
from utils import handle_fatigue_data, handle_points
import pandas as pd

def gen_train_data(stats: pd.DataFrame, features: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    X = pd.DataFrame({
        "team_label": stats["team_label"],
        "mif": stats["impact"],
        "fatigue": stats["fatigue"],
        "hours": stats["hours"],
        "weekdays": stats["weekdays"],
        "points": stats["points"],
    })

    for f in features.values():
        X[f"{f.name}_cluster"] = stats[f"{f.name}_cluster"]

        X[f"{f.name}scores_xg_ratio"] = f.results["scores_xg_ratio"]
        X[f"{f.name}mean_xg"] = f.results["mean_xg"]
        X[f"{f.name}mean_goals"] = f.results["mean_goals"]

    y = stats["created_xg"]

    return X, y

def labelers(teams: pd.DataFrame) -> dict[str, LabelEncoder]:
    team_labeler = LabelEncoder()
    team_labeler.fit(teams["id"].unique())

    return {"team": team_labeler}

def prepare_data(
    matches: pd.DataFrame, stats: pd.DataFrame, labelers: dict[str, LabelEncoder]
) -> tuple[pd.DataFrame, dict[str, SkillFeature]]:
    from feats.mif import mif_series

    matches = handle_points(matches)

    feats = get_xg_features(stats)

    matches["impact"] = mif_series(matches[["attendances"]].copy())

    # Fatigue factor
    col_fatigue = handle_fatigue_data(matches)

    stats = pd.merge(
        stats,
        col_fatigue,
        left_on=["match", "team"],
        right_on=["match_id", "team"],
        how="left",
    )

    for _, row in matches.iterrows():
        home_team_stats_id = row["teams_stats"][0]
        away_team_stats_id = row["teams_stats"][1]

        stats.loc[stats["id"] == home_team_stats_id, "played_at"] = row["played_at"]
        stats.loc[stats["id"] == away_team_stats_id, "played_at"] = row["played_at"]

        # mif
        stats.loc[stats["id"] == home_team_stats_id, "impact"] = row["impact"]
        stats.loc[stats["id"] == away_team_stats_id, "impact"] = row["impact"]

        stats.loc[stats["id"] == home_team_stats_id, "points"] = row["home_points"]
        stats.loc[stats["id"] == away_team_stats_id, "points"] = row["away_points"]

    # Time factor hours, weekdays
    stats = time_factor(stats)
    
    stats["team_label"] = labelers["team"].transform(stats["team"])

    for f in feats.values():
        f.fit()
        stats[f"{f.name}_cluster"] = f.results[f"{f.name}_cluster"]

    return stats, feats


if __name__ == "__main__":
    asyncio.run(gen_train_data())
