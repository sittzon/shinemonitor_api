from fastapi import APIRouter
from typing import List
from services.shinemonitor_service import getStatus, getEnergyNow, getEnergySummary, getEnergyTimeline, getEnergyTimelineMonth, getEnergyTimelineYear, getEnergyTimelineTotal, getPlantInfo
from schemas.index import StatusResponse, EnergyNowResponse, EnergySummaryResponse, EnergyTimelineResponse, TimelineMonthResponse, TimelineYearResponse, TimelineTotalResponse, PlantInfoResponse

router = APIRouter()

@router.get("/status", response_model=StatusResponse)
async def status():
    return getStatus()

@router.get("/now", response_model=EnergyNowResponse)
async def energy_now():
    return getEnergyNow()

@router.get("/summary", response_model=EnergySummaryResponse)
async def energy_summary():
    return getEnergySummary()

@router.get("/timeline", response_model=List[EnergyTimelineResponse])
async def energy_timeline(date: str = None):
    return getEnergyTimeline(date)

@router.get("/timeline/month", response_model=List[TimelineMonthResponse])
async def energy_timeline_month(date: str = None):
    return getEnergyTimelineMonth(date)

@router.get("/timeline/year", response_model=List[TimelineYearResponse])
async def energy_timeline_year(date: str = None):
    return getEnergyTimelineYear(date)

@router.get("/timeline/total", response_model=List[TimelineTotalResponse])
async def energy_timeline_total():
    return getEnergyTimelineTotal()

@router.get("/plantinfo", response_model=PlantInfoResponse)
async def plant_info():
    return getPlantInfo()