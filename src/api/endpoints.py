from fastapi import APIRouter
from services.shinemonitor_service import getStatus, getEnergyNow, getEnergySummary, getEnergyTimeline

router = APIRouter()

@router.get("/status")
async def status():
    return getStatus()

@router.get("/now")
async def energy_now():
    return getEnergyNow()

@router.get("/summary")
async def energy_summary():
    return getEnergySummary()

@router.get("/timeline")
async def energy_timeline():
    return getEnergyTimeline()