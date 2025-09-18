#SQLAlchemy ORM models

from sqlalchemy import Column, String, Integer
from app.database import Base

# SQLAlchemy model for storing F1 drivers. 
# Each driver is uniquely identified by driver_id -> firstname_lastname. 
# If driver_number changes, exisiting record will be updated.

class Driver(Base):
    __tablename__ = "drivers"
    
    driver_id = Column(String, primary_key=True, index=True)
    full_name = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    driver_number = Column(Integer, nullable=False)
    name_acronym = Column(String, nullable=True)
    team_name = Column(String, nullable=True)
    country_code = Column(String, nullable=True)



