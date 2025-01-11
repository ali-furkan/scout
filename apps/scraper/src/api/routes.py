from flask import Blueprint, jsonify, request
from models import Team, Match, Player, TeamStat, PlayerStat, Stadium
from .dto import (
    TeamSchema,
    MatchSchema,
    PlayerSchema,
    TeamStatsSchema,
    PlayerStatSchema,
    StadiumSchema,
)

main_bp = Blueprint("main", __name__)

@main_bp.get("/")
def hello_world():
    return {"message": "Hello, World!"}

@main_bp.get("/teams")
def get_teams():
    teams = main_bp.db_session.query(Team).all()
    ts = TeamSchema(many=True).dump(teams)
    return {"teams": ts}

@main_bp.get("/teams/<uuid:team_id>")
def get_team(team_id):
    team = main_bp.db_session.query(Team).filter_by(id=team_id).first()
    return {"team:": TeamSchema().dump(team)}

@main_bp.get("/matches")
def get_all_matches():
    limit = request.args.get("limit", default=16, type=int)
    offset = request.args.get("offset", default=0, type=int)
    matches = (
        main_bp.db_session.query(Match)
        .order_by(Match.played_at)
        .limit(limit)
        .offset(offset)
        .all()
    )
    ms = MatchSchema(many=True).dump(matches)
    return {"matches": ms}

@main_bp.get("/matches/results")
def get_played_matches():
    limit = request.args.get("limit", default=16, type=int)
    offset = request.args.get("offset", default=0, type=int)
    matches = (
        main_bp.db_session.query(Match)
        .filter_by(is_finished=True)
        .order_by(Match.played_at)
        .limit(limit)
        .offset(offset)
        .all()
    )
    ms = MatchSchema(many=True).dump(matches)
    return {"matches": ms}

@main_bp.get("/matches/fixtures")
def get_fixtures():
    limit = request.args.get("limit", default=16, type=int)
    offset = request.args.get("offset", default=0, type=int)
    matches = (
        main_bp.db_session.query(Match)
        .filter_by(is_finished=False)
        .order_by(Match.played_at)
        .limit(limit)
        .offset(offset)
        .all()
    )
    ms = MatchSchema(many=True).dump(matches)
    return {"matches": ms}

@main_bp.get("/matches/<uuid:match_id>")
def get_match(match_id):
    m = main_bp.db_session.query(Match).filter_by(id=match_id).first()
    return {"match": MatchSchema().dump(m)}

@main_bp.get("/teams/<uuid:team_id>/matches")
def get_team_matches(team_id):
    matches = main_bp.db_session.query(Match).filter(
        (Match.away_team_id == team_id) | (Match.home_team_id == team_id)
    ).all()
    ms = MatchSchema(many=True).dump(matches)
    return {"matches": ms}


@main_bp.get("/teams/<uuid:team_id>/matches/results")
def get_team_played_matches(team_id):
    matches = (
        main_bp.db_session.query(Match)
        .filter((Match.away_team_id == team_id) | (Match.home_team_id == team_id))
        .filter_by(is_finished=True)
        .order_by(Match.played_at)
        .all()
    )
    ms = MatchSchema(many=True).dump(matches)
    return {"matches": ms}


@main_bp.get("/teams/<uuid:team_id>/matches/fixtures")
def get_team_fixtures(team_id):
    matches = (
        main_bp.db_session.query(Match)
        .filter((Match.away_team_id == team_id) | (Match.home_team_id == team_id))
        .filter_by(is_finished=False)
        .order_by(Match.played_at)
        .all()
    )
    ms = MatchSchema(many=True).dump(matches)
    return {"matches": ms}

@main_bp.get("/players/<uuid:player_id>")
def get_player(player_id):
    p = main_bp.db_session.query(Player).filter_by(id=player_id).first()
    return {"player": PlayerSchema().dump(p)}

@main_bp.get("/players/<uuid:player_id>/stats")
def get_player_stats(player_id):
    stats = main_bp.db_session.query(PlayerStat).filter_by(player_id=player_id).all()
    return {"stats": PlayerStatSchema(many=True).dump(stats)}

@main_bp.get("/teams/<uuid:team_id>/stats")
def get_team_stats(team_id):
    stats = main_bp.db_session.query(TeamStat).filter_by(team_id=team_id).all()
    return {"stats": TeamStatsSchema(many=True).dump(stats)}

@main_bp.get("/stats/players")
def get_players_stats():
    limit = request.args.get("limit", default=16, type=int)
    offset = request.args.get("offset", default=0, type=int)
    stats = main_bp.db_session.query(PlayerStat).limit(limit).offset(offset).all()
    return {"stats": PlayerStatSchema(many=True).dump(stats)}

@main_bp.get("/stats/teams")
def get_teams_stats():
    limit = request.args.get("limit", default=16, type=int)
    offset = request.args.get("offset", default=0, type=int)
    stats = main_bp.db_session.query(TeamStat).limit(limit).offset(offset).all()
    return {"stats": TeamStatsSchema(many=True).dump(stats)}

@main_bp.get("/stats/teams/<uuid:stat_id>")
def get_team_stats_by_id(stat_id):
    stats = main_bp.db_session.query(TeamStat).filter_by(id=stat_id).first()
    return {"stats": TeamStatsSchema().dump(stats)}

@main_bp.get("/stats/players/<uuid:stat_id>")
def get_player_stats_by_id(stat_id):
    stats = main_bp.db_session.query(PlayerStat).filter_by(id=stat_id).first()
    return {"stats": PlayerStatSchema().dump(stats)}

@main_bp.get("/stadium/<uuid:stadium_id>")
def get_stadium(stadium_id):
    s = main_bp.db_session.query(Stadium).filter_by(id=stadium_id).first()
    return {"stadium": StadiumSchema().dump(s)}

@main_bp.get("/stadiums")
def get_stadiums():
    stadiums = main_bp.db_session.query(Stadium).all()
    return {"stadiums": StadiumSchema(many=True).dump(stadiums)}