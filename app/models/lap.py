#SQLAlchemy ORM models

from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from app.models import Base

# SQLAlchemy model for storing F1 laps. 
# Each lap is uniquely identified by ...

class Lap(Base):
    __tablename__ = "laps"

    lap_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey("races.race_id"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("sessions.session_id"), nullable=False, index=True)
    driver_number = Column(Integer, nullable=True)
    lap_number = Column(Integer, nullable=True)
    lap_duration = Column(Float, nullable=True)
    duration_sector_1 = Column(Float, nullable=True)
    duration_sector_2 = Column(Float, nullable=True)
    duration_sector_3 = Column(Float, nullable=True)
    i1_speed = Column(Float, nullable=True)
    i2_speed = Column(Float, nullable=True)
    st_speed = Column(Float, nullable=True)
    is_pit_out_lap = Column(Boolean, default=False)

    # from FastF1 library
    