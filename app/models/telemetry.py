#SQLAlchemy ORM models

from sqlalchemy import Column, Integer, Float, ForeignKey
from app.database import Base
from app.models import Base

class Telemetry(Base):
    __tablename__ = "telemetry"

    telemetry_id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey("races.race_id"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("sessions.session_id"), nullable=False, index=True)
    driver_number = Column(Integer, nullable=False)
    lap_number = Column(Integer, nullable=False)
    avg_speed = Column(Float, nullable=True)
    mean_rpm = Column(Float, nullable=True)
    median_gear = Column(Integer, nullable=True)
    throttle_usage = Column(Float, nullable=True)
    brake_usage = Column(Float, nullable=True)
    drs_usage = Column(Integer, nullable=True)


