#SQLAlchemy ORM models

from sqlalchemy import Column, String, Integer
from app.database import Base

# Driver table
class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(String, unique=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    driver_number = Column(Integer, nullable=False)
    name_acronym = Column(String, nullable=False)

