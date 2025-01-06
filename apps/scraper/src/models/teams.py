from sqlalchemy import Column, Integer, ForeignKey, String, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from models import Base, teams_matches

class Team(Base):
    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    sc_id = Column(Integer)
    name = Column(String)
    name_short = Column(String)
    slug = Column(String)
    matches = relationship("Match", secondary=teams_matches, back_populates="teams")
    players = relationship("Player", back_populates="team")
    stats = relationship("TeamStat", back_populates="team")
    stadium_id = Column(UUID(as_uuid=True), ForeignKey("stadiums.id"))
    stadium = relationship("Stadium", back_populates="team", uselist=False)
    colors = Column(JSON)
