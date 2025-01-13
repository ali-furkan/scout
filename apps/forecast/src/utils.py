import pandas as pd
from feats.fatigue_factor import fatigue_factor
from feats.skill import SkillFeature, get_xg_features
from feats.time_factor import time_factor

def handle_points(matches: pd.DataFrame) -> pd.DataFrame:
    # Create a copy of the DataFrame to avoid modifications on original
    matches = matches.copy()
    max_round = matches["round"].max()

    # Initialize columns properly
    matches = matches.assign(
        home_points=0, away_points=0, attendances=matches["attendances"].fillna(0)
    )

    for round in range(1, max_round + 1):
        # Get matches for current round
        current_round_mask = matches["round"] == round
        prev_rounds_mask = matches["round"] < round

        for p in ["home", "away"]:
            team_col = f"{p}_team"
            points_col = f"{p}_points"

            # Calculate points for each team in current round
            for idx, match in matches[current_round_mask].iterrows():
                team = match[team_col]

                # Calculate wins
                home_wins = matches[
                    prev_rounds_mask
                    & (matches["home_team"] == team)
                    & (matches["result"] == 1)
                ].shape[0]

                away_wins = matches[
                    prev_rounds_mask
                    & (matches["away_team"] == team)
                    & (matches["result"] == -1)
                ].shape[0]

                # Calculate draws
                draws = matches[
                    prev_rounds_mask
                    & ((matches["home_team"] == team) | (matches["away_team"] == team))
                    & (matches["result"] == 0)
                ].shape[0]

                # Update points using loc
                matches.loc[idx, points_col] = (home_wins + away_wins) * 3 + draws

    return matches

from sklearn.ensemble import RandomForestRegressor

def prepare(matches: pd.DataFrame, stats: pd.DataFrame) -> tuple[pd.DataFrame, RandomForestRegressor, dict[str,SkillFeature]]:
    from feats.mif import create_mif_model, mif_series
    feats = get_xg_features(stats)
    # MIF model
    matches = handle_points(matches)

    mif_data = matches[
        ["home_team", "away_team", "home_points", "away_points", "attendances"]
    ].copy()
    mif_model = create_mif_model(mif_data)
    matches["impact"] = mif_series(mif_data)

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

    # Time factor hours, weekdays
    stats = time_factor(stats)

    for f in feats.values():
        f.fit()
        stats[f"{f.name}_cluster"] = f.results[f"{f.name}_cluster"]

    return stats, mif_model, feats

def handle_fatigue_data(matches: pd.DataFrame) -> pd.DataFrame:

    matches.rename(columns={"id": "match_id"}, inplace=True)

    fatigue_data = (
        pd.concat(
            [
                matches[["match_id", "played_at", "home_team"]].rename(
                    columns={"home_team": "team"}
                ),
                matches[["match_id", "played_at", "away_team"]].rename(
                    columns={"away_team": "team"}
                ),
            ]
        )
        .drop_duplicates(subset=["match_id", "team"])
        .sort_values("played_at")
    )

    # Calculate fatigue
    return fatigue_factor(fatigue_data)
