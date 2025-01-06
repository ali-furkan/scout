from sqlalchemy import Column, Integer, ARRAY, TIMESTAMP, ForeignKey, Float, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from models import Base

class PlayerStat(Base):
    __tablename__ = "players_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    sc_id = Column(Integer)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"))
    player = relationship("Player", back_populates="stats")
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id"))
    match = relationship("Match", back_populates="players_stats")
    # Stats
    position = Column(String)
    rating = Column(Integer)
    minutes_played = Column(Integer)
    shot_off_target = Column(Integer)
    shot_on_target = Column(Integer)
    xg = Column(Float)
    xa = Column(Float)
    goals = Column(Integer)
    assists = Column(Integer)
    key_passes = Column(Integer)
    yellow_cards = Column(Integer)
    red_cards = Column(Integer)
    fouls = Column(Integer)
    touches = Column(Integer)
    rating = Column(Float)
