from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class HistoryBase(BaseModel):
    history_property_name: str
    history_date: datetime
    history_version: int
    history_change_type: str
    history_change: str

class HistoryCreate(HistoryBase):
    entity_id: int

class History(HistoryBase):
    history_id: int
    entity_id: int

    class Config:
        from_attributes = True

class TeamBase(BaseModel):
    name: str

class TeamCreate(TeamBase):
    pass

class Team(TeamBase):
    team_id: int

    class Config:
        from_attributes = True


class EntityBase(BaseModel):
    area: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    ticket_number: Optional[str] = None
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    estimation: Optional[float] = None
    spent: Optional[float] = None
    resolution: Optional[str] = None
    team_id: Optional[int]

class EntityCreate(EntityBase):
    entity_id: int

class Entity(EntityBase):
    entity_id: int
    histories: List[History] = []

    class Config:
        from_attributes = True

class SprintBase(BaseModel):
    sprint_name: str
    sprint_status: str
    start_date: datetime
    end_date: datetime

class SprintCreate(SprintBase):
    pass

class Sprint(SprintBase):
    sprint_id: int

    class Config:
        from_attributes = True
