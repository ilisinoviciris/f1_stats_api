from pydantic import BaseModel, ConfigDict
from typing import Optional

# field for Session
class SessionBase(BaseModel):
    session_id: int
    race_id: int
    session_name: Optional[str] = None
    session_type: Optional[str] = None

class SessionCreate(SessionBase):
    pass

class SessionUpdate(BaseModel):
    session_name: Optional[str] = None
    session_type: Optional[str] = None

class Session(SessionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)