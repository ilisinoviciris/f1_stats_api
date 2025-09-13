from pydantic import BaseModel

# main driver statistics
class DriverBase(BaseModel):
    driver_id: str
    first_name: str
    last_name: str
    driver_number: int
    name_acronym: str
    team_name: str

# request body
class DriverCreate(DriverBase):
    pass

# response body
class Driver(DriverBase):
    id: int

    class Config:
        orm_mode = True
