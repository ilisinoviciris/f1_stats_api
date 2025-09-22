from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .driver import Driver
from .race import Race
from .lap import Lap

__all__ = ["Driver", "Race", "Lap"]