import pandas as pd

def calculate_fatigue(days_diff, prev_fatigue) -> float:
    return max(0.0, (1.0 - (days_diff / 7.0)) * (prev_fatigue + 1.0))

def fatigue_factor(data: pd.DataFrame) -> pd.DataFrame:
    # Create a clean copy and sort by date
    d = data[["match_id", "team", "played_at"]].copy()
    d["date"] = pd.to_datetime(d["played_at"]*1000, unit='ms')
    d["fatigue"] = 0.0

    # Sort all matches by date first
    d = d.sort_values("date")

    # Process each team separately
    for team in d["team"].unique():
        # Get all matches for this team
        team_mask = d["team"] == team
        team_matches = d[team_mask].copy()

        # Initialize last game date
        last_game_date = None
        prev_fatigue = 0.0

        # Process matches in chronological order
        for idx, row in team_matches.iterrows():
            current_date = row["date"]

            if last_game_date is not None:
                # Calculate days since last game
                days_diff = (current_date - last_game_date).days
                # Calculate fatigue (1.0 means played yesterday, 0.0 means rested)
                fatigue = calculate_fatigue(days_diff, prev_fatigue)
                d.loc[idx, "fatigue"] = fatigue
                prev_fatigue = fatigue

            # Update last game date
            last_game_date = current_date

    return d[["match_id", "team", "fatigue"]]


def get_current_fatigue(last_match: pd.Series, fixture_match: pd.Series) -> float:
    # Get last match date
    last_match_date = last_match["played_at"]
    last_match_fatigue = last_match["fatigue"]

    fixture_match_date = fixture_match["played_at"]

    days_diff = (fixture_match_date - last_match_date).days

    return calculate_fatigue(days_diff, last_match_fatigue)


def current_fatigue_factor(data: pd.DataFrame) -> float:
    return data.sort_values("played_at", ascending=False).iloc[0]["fatigue"]
