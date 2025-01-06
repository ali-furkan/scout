from sqlalchemy import Column, Integer, ARRAY, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from models import Base, teams_matches

class Match(Base):
    __tablename__ = "matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    sc_id = Column(Integer)
    home_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"))
    home_team = relationship("Team", foreign_keys=[home_team_id])
    away_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"))
    away_team = relationship("Team", foreign_keys=[away_team_id])
    result = Column(Integer)
    teams_stats = relationship("TeamStat", back_populates="match")
    players_stats = relationship("PlayerStat", back_populates="match")
    stadium_id = Column(UUID(as_uuid=True), ForeignKey("stadiums.id"))
    stadium = relationship("Stadium", back_populates="played_matches")
    attendances = Column(Integer)
    referee = Column(Integer)
    played_at = Column(Integer)
    round = Column(Integer)
    is_finished = Column(Boolean, default=False)
    teams = relationship("Team", secondary=teams_matches, back_populates="matches")
