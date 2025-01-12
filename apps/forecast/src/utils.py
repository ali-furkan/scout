import pandas as pd
from feats.fatigue_factor import fatigue_factor

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
