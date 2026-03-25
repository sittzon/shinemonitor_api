from fastapi import APIRouter, HTTPException
from typing import List, Union
from datetime import datetime
from services.shinemonitor_service import getStatus, getEnergyNow, getEnergySummary, getEnergyTimeline, getEnergyTimelineMonth, getEnergyTimelineYear, getEnergyTimelineTotal, getPlantInfo
from schemas.index import StatusResponse, EnergyNowResponse, EnergySummaryResponse, EnergyTimelineResponse, TimelineMonthResponse, TimelineYearResponse, TimelineTotalResponse, PlantInfoResponse
from services.cache import get_cached, set_cached

def to_dict(obj):
    if isinstance(obj, dict):
        if "Error" in obj:
            return None
        return obj
    if hasattr(obj, 'model_dump'):
        return obj.model_dump()
    return obj

def is_today(date_str):
    if not date_str:
        return True
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        return date_obj == datetime.now().date()
    except:
        return False

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
    key = f"timeline_{date or 'today'}"
    
    if not is_today(date):
        cached = await get_cached(key)
        if cached:
            return cached
    
    result = getEnergyTimeline(date)
    if result and not is_today(date):
        await set_cached(key, [to_dict(item) for item in result], ttl=300)
    return result

@router.get("/timeline/month", response_model=List[TimelineMonthResponse])
async def energy_timeline_month(date: str = None):
    key = f"timeline_month_{date or 'current'}"
    
    if not is_today(date):
        cached = await get_cached(key)
        if cached:
            return cached
    
    result = getEnergyTimelineMonth(date)
    if result and not is_today(date):
        await set_cached(key, [to_dict(item) for item in result], ttl=300)
    return result

@router.get("/timeline/year", response_model=List[TimelineYearResponse])
async def energy_timeline_year(date: str = None):
    key = f"timeline_year_{date or 'current'}"
    
    if not is_today(date):
        cached = await get_cached(key)
        if cached:
            return cached
    
    result = getEnergyTimelineYear(date)
    if result and not is_today(date):
        await set_cached(key, [to_dict(item) for item in result], ttl=300)
    return result

@router.get("/timeline/total", response_model=List[TimelineTotalResponse])
async def energy_timeline_total():
    cached = await get_cached("timeline_total")
    if cached:
        return cached
    result = getEnergyTimelineTotal()
    if result:
        await set_cached("timeline_total", [to_dict(item) for item in result], ttl=300)
    return result

@router.get("/plant", response_model=PlantInfoResponse)
async def plant_info():
    cached = await get_cached("plant")
    if cached:
        return cached
    result = getPlantInfo()
    if result:
        await set_cached("plant", to_dict(result), ttl=3600)
    return result