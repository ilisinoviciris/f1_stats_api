#SQLAlchemy ORM models

from sqlalchemy import Column, String, Integer, ForeignKey
from app.database import Base
from app.models import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, unique=True, nullable=False, index=True)
    race_id = Column(Integer, ForeignKey("races.race_id"), nullable=False, index=True)
    session_name = Column(String, nullable=True)
    session_type = Column(String, nullable=True)