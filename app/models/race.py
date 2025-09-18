#SQLAlchemy ORM models

from sqlalchemy import Column, String, Integer
from app.database import Base

# SQLAlchemy model for storing F1 races. 
# Each race is uniquely identified by race_id 

class Race(Base):
    __tablename__ = "races"

    race_id = Column(Integer, primary_key=True, index=True)
    race_name = Column(String, index=True)
    circuit_name = Column(String, index=True)
    location = Column(String, index=True)
    country_name = Column(String, index=True)
    year = Column(Integer, index=True)
