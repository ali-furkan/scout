from sqlalchemy import Column, Integer, Boolean, ForeignKey, Float, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from models import Base

class TeamStat(Base):
    __tablename__ = "team_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"))
    team = relationship("Team", back_populates="stats")
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id"))
    match = relationship("Match", back_populates="teams_stats")
    is_overall = Column(Boolean)
    is_home = Column(Boolean)
    formation = Column(String)
    # Stats
    # Results
    goals = Column(Integer)
    assists = Column(Integer)
    rating = Column(Integer)
    possession = Column(Integer)
    # Penalties
    yellow_cards = Column(Integer)
    red_cards = Column(Integer)
    fouls = Column(Integer)
    # Dead Ball
    free_kicks = Column(Integer)
    free_kicks_in_third = Column(Integer)
    free_kicks_scored = Column(Integer)
    corners = Column(Integer)
    penalties_taken = Column(Integer)
    penalties_scored = Column(Integer)
    # Shots
    shots_on_target = Column(Integer)
    shots_off_target = Column(Integer)
    shots_inside = Column(Integer)
    shots_outside = Column(Integer)
    blocked_shots = Column(Integer)
    hit_woodwork = Column(Integer)
    created_xg = Column(Float)
    # Attacks
    big_chances_scored = Column(Integer)
    big_chances_missed = Column(Integer)
    touches_in_box = Column(Integer)
    fouled_in_third = Column(Integer)
    offsides = Column(Integer)
    # Duel
    dispossessed = Column(Integer)
    aerial_duels = Column(Integer)
    aerial_duels_success = Column(Integer)
    ground_duels = Column(Integer)
    ground_duels_success = Column(Integer)
    dribbles = Column(Integer)
    dribbles_success = Column(Integer)
    # Passing
    accurate_passes = Column(Integer)
    throw_ins = Column(Integer)
    crosses = Column(Integer)
    crosses_success = Column(Integer)
    final_third_entries = Column(Integer)
    final_third_phases = Column(Integer)
    final_third_passes_success = Column(Integer)
    long_passes = Column(Integer)
    long_passes_success = Column(Integer)
    # Defending
    tackles = Column(Integer)
    tackles_won = Column(Integer)
    interceptions = Column(Integer)
    recoveries = Column(Integer)
    clearances = Column(Integer)
    errors_leading_to_shot = Column(Integer)
    errors_leading_to_goal = Column(Integer)
    # Goalkeeping
    saves = Column(Integer)
    goal_prevented = Column(Float)
    high_claims = Column(Integer)
    punches = Column(Integer)
    goal_kicks = Column(Integer)

