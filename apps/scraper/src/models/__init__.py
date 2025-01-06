from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
Base = declarative_base()

players_matches = Table(
    "players_matches",
    Base.metadata,
    Column("player_id", UUID(as_uuid=True), ForeignKey("players.id")),
    Column("match_id", UUID(as_uuid=True), ForeignKey("matches.id")),
    Column("player_stat", UUID(as_uuid=True), ForeignKey("players_stats.id")),
)

teams_matches = Table(
    "teams_matches",
    Base.metadata,
    Column("team_id", UUID(as_uuid=True), ForeignKey("teams.id"), primary_key=True),
    Column("match_id", UUID(as_uuid=True), ForeignKey("matches.id"), primary_key=True),
)

from .players import Player
from .players_stats import PlayerStat
from .teams import Team
from .team_stats import TeamStat
from .matches import Match
from .stadiums import Stadium