import json
from datetime import datetime
import aiohttp
import os

from models import Match, PlayerStat, Player, Team, TeamStat, Stadium

from .bases import (
    ENDPOINT_STANDING,
    ENDPOINT_NEXT_MATCHES,
    ENDPOINT_FINISHED_MATCHES,
    ENDPOINT_MATCH_INFO,
    ENDPOINT_MATCH_STATS,
    ENDPOINT_MATCH_LINEUP,
    ENDPOINT_PLAYER,
    ENDPOINT_VENUE,
    ENDPOINT_TEAM,
    HEADERS,
)

def handle_result(a_goals: int, b_goals: int) -> int:
    if a_goals > b_goals:
        return 1
    elif a_goals < b_goals:
        return -1
    else:
        return 0

from config import Config
class ScraperConfig:
    @staticmethod
    def from_env() -> 'ScraperConfig':
        return ScraperConfig(
            cache_enabled=Config.cache_enabled(),
            cache_ttl=Config.cache_ttl(),
            cache_file=Config.cache_file(),
            league_id=Config.get_league_id(),
            season_id=Config.get_season_id(),
            api_url=Config.get_base_api(),
        )
    def __init__(self, cache_enabled: bool, cache_ttl: int, cache_file: str, league_id: str, season_id: str, api_url: str, headers: dict[str, str] = HEADERS):
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl
        self.cache_file = cache_file
        self.league_id = league_id
        self.season_id = season_id
        self.api_url = api_url
        self.headers = headers

class Scraper:
    def __init__(self, cfg: ScraperConfig):
        self.cache = {}
        self.config: ScraperConfig = cfg
        if os.path.exists(self.config.cache_file):
            with open(self.config.cache_file, "r") as f:
                try: 
                    self.cache = json.load(f)
                except:
                    self.cache = {}
        else:
            with open(self.config.cache_file, "w") as f:
                f.write("{}")

    def close(self):
        with open(self.config.cache_file, "w") as f:
            json.dump(self.cache, f)

    async def fetch_api(self, session: aiohttp.ClientSession ,endpoint: str, cache: bool = True) -> dict:
        if self.config.cache_enabled and cache and endpoint in self.cache:
            c = self.cache[endpoint]
            if (datetime.now().timestamp() - c["timestamp"]) < self.config.cache_ttl:
                return c["data"]
            else:
                del self.cache[endpoint]

        url = f"{self.config.api_url}{endpoint}"
        async with session.get(url, headers=self.config.headers) as res:
            status = res.status
            data = await res.json()
            if status != 200:
                raise Exception(f"{endpoint} - Request failed with status code {status}")

            self.cache[endpoint] = {
                "timestamp": datetime.now().timestamp(),
                "data": data
            }
            return data

    async def fetch_match(self, match: Match) -> Match:
        if not match.sc_id:
            raise Exception("Match has no sc_id")

        # fetching match info
        data_info = None
        data_stats = None
        data_lineup = None
        async with aiohttp.ClientSession() as session:
            data_info = await self.fetch_api(session,ENDPOINT_MATCH_INFO.format(match_id=match.sc_id))
            data_stats = await self.fetch_api(session,ENDPOINT_MATCH_STATS.format(match_id=match.sc_id))
            data_lineup = await self.fetch_api(session,ENDPOINT_MATCH_LINEUP.format(match_id=match.sc_id))

        info = data_info["event"] 

        match.attendances = info.get("attendance", 0)
        match.referee = info["referee"]["id"]
        match.result = handle_result(
            info["homeScore"]["current"], info["awayScore"]["current"]
        )

        stats = data_stats["statistics"][0]["groups"]
        from .bases import (
            key_map,
            doubled_key_map,
            ha_score_map,
            ha_val_map,
            ha_tot_map,
        )

        feats: dict[str, list] = {}
        i = 0
        for m in [key_map, doubled_key_map]:
            for k in m:
                feats[k] = [0, 0]
                if i == 1:
                    feats[f"{k}Total"] = [0, 0]
                for stat_group in stats:
                    items = stat_group["statisticsItems"]
                    for item in items:
                        if item["key"] == k:
                            feats[k][0] = item[ha_val_map[0]]
                            feats[k][1] = item[ha_val_map[1]]
                            if i == 1:
                                feats[f"{k}Total"][0] = item[ha_tot_map[0]]
                                feats[f"{k}Total"][1] = item[ha_tot_map[1]]
            i += 1

        feats["goals"] = [
            info[ha_score_map[0]]["current"],
            info[ha_score_map[1]]["current"],
        ]
        feats["formation"] = [
            data_lineup["home"]["formation"],
            data_lineup["away"]["formation"],
        ]
        match.teams_stats = self.handle_team_stats(match, feats)

        for team in data_lineup["home"], data_lineup["away"]:
            for player in team["players"]:
                ps = PlayerStat(
                    sc_id=player["player"]["id"],
                    match_id=match.id,
                    position=player["position"],
                    minutes_played=player["statistics"].get("minutesPlayed", 0),
                    xg=player["statistics"].get("expectedGoals", 0.0),
                    xa=player["statistics"].get("expectedAssists", 0.0),
                    goals=player["statistics"].get("goals", 0),
                    assists=player["statistics"].get("goalAssist", 0),
                    key_passes=player["statistics"].get("keyPass", 0),
                    yellow_cards=player["statistics"].get("yellowCards", 0),
                    red_cards=player["statistics"].get("redCards", 0),
                    shot_off_target=player["statistics"].get("shotOffTarget", 0),
                    shot_on_target=player["statistics"].get(
                        "onTargetScoringAttempt", 0
                    ),
                    touches=player["statistics"].get("touches", 0),
                    fouls=player["statistics"].get("fouls", 0),
                    rating=player["statistics"].get("rating", 0.0),
                )
                match.players_stats.append(ps)

        return match

    def handle_team_stats(self, match: Match, data: dict) -> list[TeamStat]:
        stats = []
        i = 0
        for t in [match.home_team, match.away_team]:
            ts = TeamStat(
                team=t,
                match=match,
                formation=data["formation"][i],
                is_overall=False,
                is_home=(i == 0),
                goals=data["goals"][i],
                possession=data["ballPossession"][i],
                yellow_cards=data["yellowCards"][i],
                red_cards=data["redCards"][i],
                fouls=data["fouls"][i],
                free_kicks=data["freeKicks"][i],
                corners=data["cornerKicks"][i],
                shots_on_target=data["shotsOnGoal"][i],
                shots_off_target=data["shotsOffGoal"][i],
                shots_inside=data["totalShotsInsideBox"][i],
                shots_outside=data["totalShotsOutsideBox"][i],
                blocked_shots=data["blockedScoringAttempt"][i],
                hit_woodwork=data["hitWoodwork"][i],
                created_xg=data["expectedGoals"][i],
                big_chances_scored=data["bigChanceScored"][i],
                big_chances_missed=data["bigChanceMissed"][i],
                touches_in_box=data["touchesInOppBox"][i],
                fouled_in_third=data["fouledFinalThird"][i],
                offsides=data["offsides"][i],
                dispossessed=data["dispossessed"][i],
                aerial_duels=data["aerialDuelsPercentageTotal"][i],
                aerial_duels_success=data["aerialDuelsPercentage"][i],
                ground_duels=data["groundDuelsPercentageTotal"][i],
                ground_duels_success=data["groundDuelsPercentage"][i],
                dribbles=data["dribblesPercentageTotal"][i],
                dribbles_success=data["dribblesPercentage"][i],
                accurate_passes=data["accuratePasses"][i],
                throw_ins=data["throwIns"][i],
                crosses=data["accurateCrossTotal"][i],
                crosses_success=data["accurateCross"][i],
                final_third_entries=data["finalThirdEntries"][i],
                final_third_phases=data["finalThirdPhaseStatisticTotal"][i],
                final_third_passes_success=data["finalThirdPhaseStatistic"][i],
                long_passes=data["accurateLongBallsTotal"][i],
                long_passes_success=data["accurateLongBalls"][i],
                tackles=data["totalTackle"][i],
                tackles_won=data["wonTacklePercent"][i],
                interceptions=data["interceptions"][i],
                recoveries=data["ballRecovery"][i],
                clearances=data["totalClearance"][i],
                errors_leading_to_shot=data["errorsLeadToShot"][i],
                errors_leading_to_goal=data["errorsLeadToGoal"][i],
                saves=data["goalkeeperSaves"][i],
                goal_prevented=data["goalsPrevented"][i],
                high_claims=data["highClaims"][i],
                punches=data["punches"][i],
                goal_kicks=data["goalKicks"][i],
            )
            stats.append(ts)
            i += 1
        return stats

    async def fetch_teams(self) -> list[Team]:
        data = None
        async with aiohttp.ClientSession() as session:
            data = await self.fetch_api(
                session,
                ENDPOINT_STANDING.format(league_id=self.config.league_id, season_id=self.config.season_id),
            )

        teams_rows = data["standings"][0]["rows"]
        teams = list[Team]()
        for t in teams_rows:
            team = Team(
                sc_id=t["team"]["id"],
                name=t["team"]["name"],
                slug=t["team"]["slug"],
                name_short=t["team"]["nameCode"],
            )
            teams.append(team)

        return teams

    async def fetch_matches(self, teams: list[Team], next_matches: bool = False) -> list[Match]:
        matches = []
        for team in teams:
            ms = await self.fetch_team_matches(team, next_matches=next_matches)
            for match in ms:
                if match.sc_id not in [m.sc_id for m in matches]:
                    match.home_team = list(filter(
                        lambda t: t.sc_id == match.home_team_id, teams
                    ))[0]
                    match.away_team = list(filter(
                        lambda t: t.sc_id == match.away_team_id, teams
                    ))[0]
                    match.home_team_id = None
                    match.away_team_id = None
                    matches.append(match)

        return matches

    async def fetch_team_matches(self, team: Team , next_matches: bool = False) -> list[Match]:
        if not team.sc_id:
            raise Exception("Team has no sc_id")

        matches: list[Match] = []

        is_next_page_available = True
        page = 0
        from config import Config

        LEAGUE_ID = Config.get_league_id()
        SEASON_ID = Config.get_season_id()
        endpoint = ENDPOINT_NEXT_MATCHES if next_matches else ENDPOINT_FINISHED_MATCHES

        async with aiohttp.ClientSession() as session:
            while is_next_page_available:
                data = await self.fetch_api(session,endpoint.format(team_id=team.sc_id, page=page))
                is_next_page_available = data["hasNextPage"]
                page += 1
                added_matches = 0
                for m in data["events"]:
                    if m["tournament"]["uniqueTournament"]["id"] == LEAGUE_ID and m["season"]["id"] == SEASON_ID:
                        added_matches += 1
                        match = Match(
                            sc_id=m["id"],
                            home_team_id=m["homeTeam"]["id"],
                            away_team_id=m["awayTeam"]["id"],
                            played_at=m["startTimestamp"],
                            is_finished=m["status"]["type"] == "finished",
                            round=m["roundInfo"]["round"],
                        )
                        matches.append(match)
                if added_matches == 0:
                    return matches

        return matches

    async def fetch_player(self, sc_id: int) -> Player:
        data = None
        async with aiohttp.ClientSession() as session:
            data = await self.fetch_api(session,ENDPOINT_PLAYER.format(player_id=sc_id))

        player = Player()

        player.name = data["player"]["name"]
        player.sc_id = data["player"]["id"]
        player.team_sid = data["player"]["team"]["id"]
        player.position = data["player"]["position"]
        player.country = data["player"]["country"]["alpha3"]
        player.number = data["player"]["shirtNumber"]
        player.date_bd = data["player"]["dateOfBirthTimestamp"]
        player.preferred_foot = data["player"].get("preferredFoot", "unknown")

        return player

    async def fetch_team_features(self, team: Team) -> Team:
        data = None
        async with aiohttp.ClientSession() as session:
            data = await self.fetch_api(session,ENDPOINT_TEAM.format(team_id=team.sc_id))

        if team.colors is None:
            team.colors = data["team"]["teamColors"]
        if team.stadium is None:
            await self.fetch_team_stadium(team)

        return team

    async def fetch_team_stadium(self, team: Team) -> Stadium:
        data = None
        async with aiohttp.ClientSession() as session:
            data = await self.fetch_api(
                session, ENDPOINT_TEAM.format(team_id=team.sc_id)
            )

        stadium = Stadium()

        stadium.sc_id = data["team"]["venue"]["id"]
        stadium.name = data["team"]["venue"]["name"]
        stadium.slug = data["team"]["venue"]["slug"]
        stadium.capacity = data["team"]["venue"]["capacity"]
        stadium.city = data["team"]["venue"]["city"]["name"]
        coord = list(
            data["team"]["venue"]
            .get("venueCoordinates", {"latitude": 0, "longitude": 0})
            .values()
        )
        stadium.latitude = coord[0]
        stadium.longitude = coord[1]
        team.stadium = stadium

        return stadium

    async def fetch_stadium(self, sc_id: int) -> Stadium:
        data = None
        async with aiohttp.ClientSession() as session:
            data = await self.fetch_api(session,ENDPOINT_VENUE.format(venue_id=sc_id), cache=False)

        stadium = Stadium()

        stadium.sc_id = data["venue"]["id"]
        stadium.name = data["venue"]["name"]
        stadium.slug = data["venue"]["slug"]
        stadium.capacity = data["venue"]["capacity"]
        stadium.city = data["venue"]["city"]["name"]
        coord = list(
            data["venue"]
            .get("venueCoordinates", {"latitude": 0, "longitude": 0})
            .values()
        )
        stadium.latitude = coord[0]
        stadium.longitude = coord[1]

        return stadium
