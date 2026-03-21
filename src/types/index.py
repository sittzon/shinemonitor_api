from pydantic import BaseModel
from typing import Optional

class EnergySummaryResponse(BaseModel):
    Today: float
    Month: float
    Year: float
    Total: float
    Unit: str

class EnergyNowResponse(BaseModel):
    TimeStamp: str
    Energy: float
    Unit: str

class StatusResponse(BaseModel):
    Status: str

class EnergyTimelineResponse(BaseModel):
    TimeStamp: str
    Value: float
    Unit: str