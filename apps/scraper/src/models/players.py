from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from models import Base

class Player(Base):
    __tablename__ = "players"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String)
    sc_id = Column(Integer)
    team_sid = Column(Integer)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"))
    team = relationship("Team", back_populates="players")
    stats = relationship("PlayerStat", back_populates="player")
    position = Column(String)
    country = Column(String)
    number = Column(Integer)
    date_bd = Column(Integer)
    preferred_foot = Column(String)
