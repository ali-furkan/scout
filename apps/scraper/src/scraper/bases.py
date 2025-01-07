ENDPOINT_STANDING = "/unique-tournament/{league_id}/season/{season_id}/standings/total"
ENDPOINT_NEXT_MATCHES = "/team/{team_id}/events/next/{page}"
ENDPOINT_FINISHED_MATCHES = "/team/{team_id}/events/last/{page}"
ENDPOINT_MATCH_INFO = "/event/{match_id}"
ENDPOINT_MATCH_STATS = "/event/{match_id}/statistics"
ENDPOINT_MATCH_LINEUP = "/event/{match_id}/lineups"
ENDPOINT_PLAYER = "/player/{player_id}"
ENDPOINT_VENUE = "/venue/{venue_id}"
ENDPOINT_TEAM = "/team/{team_id}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

ha_score_map = ["homeScore", "awayScore"]
ha_val_map = ["homeValue", "awayValue"]
ha_tot_map = ["homeTotal", "awayTotal"]
key_map = [
    "ballPossession",
    "yellowCards",
    "redCards",
    "fouls",
    "cornerKicks",
    "freeKicks",
    "shotsTotal",
    "shotsOnGoal",
    "shotsOffGoal",
    "totalShotsInsideBox",
    "totalShotsOutsideBox",
    "blockedScoringAttempt",
    "hitWoodwork",
    "expectedGoals",
    "bigChanceScored",
    "bigChanceMissed",
    "touchesInOppBox",
    "fouledFinalThird",
    "offsides",
    "accuratePasses",
    "throwIns",
    "finalThirdEntries",
    "dispossessed",
    "wonTacklePercent",
    "totalTackle",
    "interceptions",
    "ballRecovery",
    "totalClearance",
    "errorsLeadToShot",
    "errorsLeadToGoal",
    "goalkeeperSaves",
    "goalsPrevented",
    "highClaims",
    "punches",
    "goalKicks",
]
doubled_key_map = [
    "finalThirdPhaseStatistic",
    "accurateLongBalls",
    "accurateCross",
    "aerialDuelsPercentage",
    "groundDuelsPercentage",
    "dribblesPercentage",
]
