import pandas as pd
from feats.fatigue_factor import fatigue_factor

from fetch import fetch
import aiohttp

async def fetch_match_history():
    matches: pd.DataFrame
    stats: pd.DataFrame

    async with aiohttp.ClientSession() as session:
        data_matches = await fetch(session, "/matches/results?limit=400")
        data_stats = await fetch(session, "/stats/teams?limit=400")

        matches = pd.DataFrame(data_matches["matches"])
        stats = pd.DataFrame(data_stats["stats"])

    return matches, stats

async def fetch_fixtures():
    fixtures: pd.DataFrame = None
    async with aiohttp.ClientSession() as session:
        data_fixtures = await fetch(session, "/matches/fixtures")
  
        fixtures_data = data_fixtures.get('matches', None)
        
        if not fixtures_data:
            raise ValueError("No fixtures data received from API")
            
        fixtures = pd.DataFrame(fixtures_data)

    return fixtures

def handle_team_points(team_id: str,matches: pd.DataFrame) -> int:
    m = matches.copy()
    home_wins = m[(m["home_team"] == team_id) & (m["result"] == 1)].shape[0]
    away_wins = m[(m["away_team"] == team_id) & (m["result"] == -1)].shape[0]
    draws = m[((m["home_team"] == team_id) | (m["away_team"] == team_id)) & (m["result"] == 0)].shape[0]

    return (home_wins + away_wins) * 3 + draws

async def fetch_teams() -> pd.DataFrame:
    teams: pd.DataFrame = None
    async with aiohttp.ClientSession() as session:
        data_teams = await fetch(session, "/teams")

        teams_data = data_teams.get('teams', None)
        
        if not teams_data:
            raise ValueError("No teams data received from API")
            
        teams = pd.DataFrame(teams_data)

    return teams


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
    m = matches.copy()

    m.rename(columns={"id": "match_id"}, inplace=True)

    fatigue_data = (
        pd.concat(
            [
                m[["match_id", "played_at", "home_team"]].rename(
                    columns={"home_team": "team"}
                ),
                m[["match_id", "played_at", "away_team"]].rename(
                    columns={"away_team": "team"}
                ),
            ]
        )
        .drop_duplicates(subset=["match_id", "team"])
        .sort_values("played_at")
    )

    # Calculate fatigue
    return fatigue_factor(fatigue_data)


def handle_fixture(l_home, l_away) -> dict:
    from scipy.stats import poisson
    max_goals = 8

    home_goal_probs = [poisson.pmf(k, l_home) for k in range(max_goals)]
    away_goal_probs = [poisson.pmf(k, l_away) for k in range(max_goals)]

    draw_probs = sum(home_goal_probs[k] * away_goal_probs[k] for k in range(max_goals))

    home_win_prob = sum(
        home_goal_probs[i] * sum(away_goal_probs[j] for j in range(i))
        for i in range(1, max_goals)
    )
    away_win_prob = sum(
        away_goal_probs[i] * sum(home_goal_probs[j] for j in range(i))
        for i in range(1, max_goals)
    )

    return {
        "home_win_prob": home_win_prob,
        "away_win_prob": away_win_prob,
        "draw_prob": draw_probs,
        "probabilities": {
            "home": home_goal_probs,
            "away": away_goal_probs,
        },
    }
