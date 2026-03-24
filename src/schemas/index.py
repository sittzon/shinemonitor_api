from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EnergySummaryResponse(BaseModel):
    Today: float
    Month: float
    Year: float
    Total: float
    Unit: str

class EnergyNowResponse(BaseModel):
    TimeStamp: datetime
    Energy: float
    Unit: str

class StatusResponse(BaseModel):
    Status: str

class EnergyTimelineResponse(BaseModel):
    TimeStamp: datetime
    Value: float
    Unit: str

class TimelineMonthResponse(BaseModel):
    TimeStamp: datetime
    Value: float
    Unit: str

class TimelineYearResponse(BaseModel):
    TimeStamp: datetime
    Value: float
    Unit: str

class TimelineTotalResponse(BaseModel):
    TimeStamp: datetime
    Value: float
    Unit: str

class PlantAddress(BaseModel):
    address: str
    city: str
    country: str
    county: str
    lat: str
    lon: str
    province: str
    timezone: int

class PlantProfit(BaseModel):
    co2: str
    coal: str
    consProfit: float
    currency: str
    feedProfit: float
    purchProfit: float
    selfProfit: float
    so2: str
    soldProfit: float
    unitProfit: str

class PlantInfoResponse(BaseModel):
    name: str
    capacity: str
    location: str
    latitude: str
    longitude: str
    installDate: str
    gridConnectionDate: str
    nominalPower: Optional[str] = None
    energyYearEstimate: Optional[str] = None
    status: Optional[int] = None
    pid: Optional[int] = None
    uid: Optional[int] = None
    address: Optional[PlantAddress] = None
    profit: Optional[PlantProfit] = None
    energyOffset: Optional[float] = None
    gts: Optional[str] = None
    flag: Optional[bool] = None