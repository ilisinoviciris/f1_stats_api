from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .driver import Driver
from .race import Race

__all__ = ["Driver", "Race"]