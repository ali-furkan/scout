from sqlalchemy import Column, Integer, ARRAY, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from sqlalchemy.orm import relationship
from models import Base

class Stadium(Base):
    __tablename__ = "stadiums"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    sc_id = Column(Integer, unique=True)
    name = Column(String)
    played_matches = relationship("Match", back_populates="stadium")
    capacity = Column(Integer)
    city = Column(String)
    slug = Column(String)
    team = relationship("Team", back_populates="stadium", uselist=False)
