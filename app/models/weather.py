#SQLAlchemy ORM models

from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey, UniqueConstraint
from app.database import Base
from app.models import Base

class Weather(Base):
    __tablename__ = "weather"

    weather_id = Column(Integer, primary_key=True, index=True)

    race_id = Column(Integer, ForeignKey("races.race_id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.session_id"), nullable=False)
    air_temp = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)
    rainfall = Column(Boolean, nullable=True)
    track_temp = Column(Float, nullable=True)
    wind_direction = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)


    __table_args__ = (
        UniqueConstraint("race_id", 
                         "session_id", 
                         name="uq_weather_session"
        ),
    )