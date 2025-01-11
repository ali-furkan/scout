from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from models import Team, TeamStat, Match, Player, PlayerStat, Stadium


class TeamSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Team
        load_instance = True
        include_relationships = True


class TeamStatsSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TeamStat
        load_instance = True
        include_relationships = True

class MatchSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Match
        load_instance = True
        include_relationships = True


class PlayerSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Player
        load_instance = True
        include_relationships = True

class PlayerStatSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PlayerStat
        load_instance = True
        include_relationships = True

class StadiumSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Stadium
        load_instance = True
        include_relationships = True