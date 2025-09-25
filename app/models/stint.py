#SQLAlchemy ORM models

from sqlalchemy import Column, String, Integer, ForeignKey
from app.database import Base
from app.models import Base

class Stint(Base):
    __tablename__ = "stints"

    stint_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey("races.race_id"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("sessions.session_id"), nullable=False, index=True)
    driver_number = Column(Integer, nullable=False, index=True)
    stint_number = Column(Integer, nullable=False)
    lap_start = Column(Integer, nullable=True)
    lap_end = Column(Integer, nullable=True)
    tyre_compound = Column(String, nullable=True)