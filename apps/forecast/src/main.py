import aiohttp
import asyncio
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder

from feats.mif import create_mif_model, mif_series
from feats.time_factor import time_factor
from utils import handle_points, handle_fatigue_data

async def fetch(session: aiohttp.ClientSession, endpoint):
    async with session.get(f"http://127.0.0.1:5000{endpoint}") as response:
        return await response.json()

    return matches

def prepare_data(matches: pd.DataFrame,stats: pd.DataFrame) -> pd.DataFrame:
    # MIF model
    matches = handle_points(matches)

    mif_data = matches[
        ["home_team", "away_team", "home_points", "away_points", "attendances"]
    ].copy()
    mif_model = create_mif_model(mif_data)
    matches["impact"] = mif_series(mif_data)

    # Fatigue factor
    col_fatigue = handle_fatigue_data(matches)

    # Merge fatigue data back to stats "fatigue"
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

    # Time factor hours, weekdays
    stats = time_factor(stats)

    return stats


async def main():
    matches = None
    fixtures = None
    stats = None

    async with aiohttp.ClientSession() as session:
        data_matches = await fetch(session,"/matches/results?limit=400")
        data_fixtures = await fetch(session,"/matches/fixtures?limit=400")
        data_stats = await fetch(session, "/stats/teams?limit=400")

        matches = pd.DataFrame(data_matches["matches"])
        fixtures = pd.DataFrame(data_matches["matches"])
        stats = pd.DataFrame(data_stats["stats"])


    stats = prepare_data(matches.copy(), stats.copy())

    X = pd.DataFrame({
        "mif": stats["impact"],
        "fatigue": stats["fatigue"],
        "hours": stats["hours"],
        "weekdays": stats["weekdays"],
    })

    print(X)


if __name__ == '__main__':
    asyncio.run(main())
