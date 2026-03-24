#!/usr/bin/python3
import urllib, hashlib
from urllib.request import urlopen
from pprint import pprint
import requests
import json
import time
from datetime import datetime, timedelta
import config as config
import re
import sys
from enums import Action
from schemas.index import EnergySummaryResponse, EnergyNowResponse, StatusResponse, EnergyTimelineResponse, TimelineMonthResponse, TimelineYearResponse, TimelineTotalResponse, PlantInfoResponse, PlantAddress, PlantProfit
from typing import List

def parse_timestamp(ts_str):
    try:
        return datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            return datetime.strptime(ts_str, '%Y-%m-%d')
        except ValueError:
            return datetime.strptime(ts_str, '%Y-%m')

def salt():
    return int(round(time.time() * 1000))

def requestToken(salt):
  #Build auth url
  powSha1=hashlib.sha1()
  powSha1.update(config.pwd.encode('utf-8'))
  action= '&action=auth&usr='+str(config.usr)+'&company-key='+str(config.companykey);
  pwdaction= str(salt) + str(powSha1.hexdigest()) + action  #This complete string needs SHA1
  auth_sign=hashlib.sha1()
  auth_sign.update(pwdaction.encode('utf-8'))
  sign = str(auth_sign.hexdigest())
  solarurl= baseURL+'?sign='+sign+'&salt='+str(salt)+action
  print(solarurl)
  r = requests.get(solarurl)
  pprint(r.json())
  token=r.json()['dat']['token']
  secret=r.json()['dat']['secret']
  expire=r.json()['dat']['expire']
  #Convert expire to datetime when expiring
  d = datetime.now().today()
  expire = d + timedelta(seconds=expire)
  return token, secret, expire

def buildRequestUrl(action: Action, salt, secret, token, devcode, plantId, pn, sn, date=None):
  if action == Action.SUMMARY:
    action_params = '&action=queryPlantCurrentData&plantid='+plantId+'&par=ENERGY_TODAY,ENERGY_MONTH,ENERGY_YEAR,ENERGY_TOTAL'#,ENERGY_PROCEEDS,ENERGY_CO2,CURRENT_TEMP,CURRENT_RADIANT,BATTERY_SOC,ENERGY_COAL,ENERGY_SO2'
  elif action == Action.TIMELINE_DAY:
    date_str = date if date else datetime.today().strftime('%Y-%m-%d')
    action_params = '&action=queryPlantActiveOuputPowerOneDay&plantid='+plantId+'&date=' + date_str
  elif action == Action.TIMELINE_MONTH:
    date_str = date if date else datetime.today().strftime('%Y-%m')
    action_params = '&action=queryPlantEnergyMonthPerDay&plantid='+plantId+'&date='+ date_str
  elif action == Action.TIMELINE_YEAR:
    date_str = date if date else datetime.today().strftime('%Y')
    action_params = '&action=queryPlantEnergyYearPerMonth&plantid='+plantId+'&date='+ date_str
  elif action == Action.TIMELINE_TOTAL:
    action_params = '&action=queryPlantEnergyTotalPerYear&plantid='+plantId
  elif action == Action.PLANT_INFO:
    action_params = '&action=queryPlantInfo&plantid='+plantId
  elif action == Action.ENERGY_TODAY:
    action_params = '&action=queryDeviceDataOneDayPaging&devaddr=1&pn='+pn+'&devcode='+devcode+'&sn='+sn+'&date='+datetime.today().strftime('%Y-%m-%d')#+'&page=0&pagesize=50&i18n=en_US&lang=en_US'
  elif action == Action.STATUS:
    action_params = '&action=queryPlantDeviceDesignatedInformation&plantid='+plantId+'&devtype=512'#&i18n=en_US&parameter=energy_today,energy_total&i18n=en_US&lang=en_US'

  reqaction= str(salt) + secret + token + action_params
  req_sign=hashlib.sha1()
  req_sign.update(reqaction.encode('utf-8'))
  sign = str(req_sign.hexdigest())
  requrl= baseURL + '?sign='+ sign + '&salt=' + str(salt) + '&token=' + token + action_params
  return requrl

def make_request(action: Action, date=None):
  token, secret = getToken()
  salt_val = salt()
  requrl = buildRequestUrl(action, str(salt_val), secret, token, config.devcode, config.plantId, config.pn, config.sn, date)
  if config.debug == 1:
    print(requrl)
  r = requests.get(requrl)
  try:
      json_data = r.json()
      errcode = json_data.get('err', -1)
      if errcode != 0:
          if config.debug == 1:
              print(f'Errorcode {errcode}')
              pprint(json_data)
          return None, errcode
      return json_data, 0
  except json.JSONDecodeError:
      if config.debug == 1:
          print("Failed to decode JSON response")
      return None, -1

baseURL = 'http://web.shinemonitor.com/public/'

#Use token if exists
def getToken():
  token, secret, expire = '','',''
  try:
    f = open("token", "r")
    if config.debug == 1:
      print("Using tokenfile credentials")
    token = f.readline().strip()
    secret= f.readline().strip()
    expire= f.readline().strip()
    #Check if token expired
    d = datetime.now().today()
    e = datetime.strptime(expire, '%Y-%m-%d %H:%M:%S.%f')
    if config.debug == 1:
      print("Datetime now:  "+str(d))
      print("Expires:       "+str(e))
    if(d > e):
      if config.debug == 1:
        print("Expired")
      raise Exception("Token expired")
    else:
      if config.debug == 1:
        print("Not expired")
  except:
    if config.debug == 1:
      print("Logging in using credentials")
    token, secret, expire = requestToken(salt())
    f = open("token", "w")
    f.write(token+'\n')
    f.write(secret+'\n')
    f.write(str(expire))
    f.close()
  finally:
    try:
        f.close()
    except NameError:
        pass
  return token, secret

def getStatus():
  json_data, errcode = make_request(Action.STATUS)
  if errcode == 0 and json_data is not None:
    status=json_data['dat']['device'][0]['status']
    if (status == 0):
      status = "Online"
    else:
      status = "Offline"
    return StatusResponse(Status=status)
  else:
    return {"Error": str(errcode)}

def getEnergyNow():
  json_data, errcode = make_request(Action.ENERGY_TODAY)
  if errcode == 0 and json_data is not None:
    timestamp=json_data['dat']['row'][0]['field'][1]
    energy_now=json_data['dat']['row'][0]['field'][5]
    timestamp_dt = datetime.strptime(str(timestamp), '%Y-%m-%d %H:%M:%S')
    return EnergyNowResponse(TimeStamp=timestamp_dt, Energy=float(energy_now), Unit="W")
  else:
    return {"Error": str(errcode)}

def getEnergySummary():
  json_data, errcode = make_request(Action.SUMMARY)
  if errcode == 0 and json_data is not None:
    energy_today=json_data['dat'][0]['val']
    energy_month=json_data['dat'][1]['val']
    energy_year=json_data['dat'][2]['val']
    energy_total=json_data['dat'][3]['val']
    return EnergySummaryResponse(Today=float(energy_today), Month=float(energy_month), Year=float(energy_year), Total=float(energy_total), Unit="kWh")
  else:
    return {"Error": str(errcode)}

def getEnergyTimeline(date=None):
  json_data, errcode = make_request(Action.TIMELINE_DAY, date)
  if errcode == 0 and json_data is not None:
    energy_over_day=json_data['dat']['outputPower']
    energy_over_day=re.sub(r'\'','"',str(energy_over_day))
    energy_over_day=re.sub(r'("val":\ )"([\d\.]+)"',r'\1\2',str(energy_over_day))
    energy_over_day=re.sub(r'"val"','"Value"',str(energy_over_day))
    energy_over_day=re.sub(r'"ts"','"TimeStamp"',str(energy_over_day))
    energy_over_day=re.sub(r'}',', "Unit": "kW"}',str(energy_over_day))
    data = json.loads(energy_over_day)
    return [EnergyTimelineResponse(TimeStamp=parse_timestamp(item['TimeStamp']), Value=item['Value'], Unit=item['Unit']) for item in data]
  else:
    print('Errorcode '+str(errcode))
    if json_data is not None:
        pprint(json_data)

def getEnergyTimelineMonth(date=None):
  json_data, errcode = make_request(Action.TIMELINE_MONTH, date)
  if errcode == 0 and json_data is not None:
    energy_over_month=json_data['dat']['perday']
    energy_over_month=re.sub(r'\'','"',str(energy_over_month))
    energy_over_month=re.sub(r'("val":\ )"([\d\.]+)"',r'\1\2',str(energy_over_month))
    energy_over_month=re.sub(r'"val"','"Value"',str(energy_over_month))
    energy_over_month=re.sub(r'"ts"','"TimeStamp"',str(energy_over_month))
    energy_over_month=re.sub(r'}',', "Unit": "kWh"}',str(energy_over_month))
    data = json.loads(energy_over_month)
    return [TimelineMonthResponse(TimeStamp=parse_timestamp(item['TimeStamp']), Value=item['Value'], Unit=item['Unit']) for item in data]
  else:
    print('Errorcode '+str(errcode))
    if json_data is not None:
        pprint(json_data)

def getEnergyTimelineYear(date=None):
  json_data, errcode = make_request(Action.TIMELINE_YEAR, date)
  if errcode == 0 and json_data is not None:
    energy_over_year=json_data['dat']['permonth']
    energy_over_year=re.sub(r'\'','"',str(energy_over_year))
    energy_over_year=re.sub(r'("val":\ )"([\d\.]+)"',r'\1\2',str(energy_over_year))
    energy_over_year=re.sub(r'"val"','"Value"',str(energy_over_year))
    energy_over_year=re.sub(r'"ts"','"TimeStamp"',str(energy_over_year))
    energy_over_year=re.sub(r'}',', "Unit": "kWh"}',str(energy_over_year))
    data = json.loads(energy_over_year)
    return [TimelineYearResponse(TimeStamp=parse_timestamp(item['TimeStamp']), Value=item['Value'], Unit=item['Unit']) for item in data]
  else:
    print('Errorcode '+str(errcode))
    if json_data is not None:
        pprint(json_data)

def getEnergyTimelineTotal():
  json_data, errcode = make_request(Action.TIMELINE_TOTAL)
  if errcode == 0 and json_data is not None:
    energy_over_total=json_data['dat']['peryear']
    energy_over_total=re.sub(r'\'','"',str(energy_over_total))
    energy_over_total=re.sub(r'("val":\ )"([\d\.]+)"',r'\1\2',str(energy_over_total))
    energy_over_total=re.sub(r'"val"','"Value"',str(energy_over_total))
    energy_over_total=re.sub(r'"ts"','"TimeStamp"',str(energy_over_total))
    energy_over_total=re.sub(r'}',', "Unit": "kWh"}',str(energy_over_total))
    data = json.loads(energy_over_total)
    return [TimelineTotalResponse(TimeStamp=parse_timestamp(item['TimeStamp']), Value=item['Value'], Unit=item['Unit']) for item in data]
  else:
    print('Errorcode '+str(errcode))
    if json_data is not None:
        pprint(json_data)

def getPlantInfo():
  json_data, errcode = make_request(Action.PLANT_INFO)
  if errcode == 0 and json_data is not None:
    dat = json_data.get('dat', {})
    address_data = dat.get('address', {})
    profit_data = dat.get('profit', {})
    
    address = PlantAddress(
        address=address_data.get('address', ''),
        city=address_data.get('city', ''),
        country=address_data.get('country', ''),
        county=address_data.get('county', ''),
        lat=address_data.get('lat', ''),
        lon=address_data.get('lon', ''),
        province=address_data.get('province', ''),
        timezone=address_data.get('timezone', 0)
    ) if address_data else None
    
    profit = PlantProfit(
        co2=profit_data.get('co2', ''),
        coal=profit_data.get('coal', ''),
        consProfit=profit_data.get('consProfit', 0.0),
        currency=profit_data.get('currency', ''),
        feedProfit=profit_data.get('feedProfit', 0.0),
        purchProfit=profit_data.get('purchProfit', 0.0),
        selfProfit=profit_data.get('selfProfit', 0.0),
        so2=profit_data.get('so2', ''),
        soldProfit=profit_data.get('soldProfit', 0.0),
        unitProfit=profit_data.get('unitProfit', '')
    ) if profit_data else None
    
    return PlantInfoResponse(
        name=dat.get('name', ''),
        capacity=dat.get('capacity', ''),
        location=dat.get('location', ''),
        latitude=address_data.get('lat', '') if address_data else '',
        longitude=address_data.get('lon', '') if address_data else '',
        installDate=dat.get('install', ''),
        gridConnectionDate=dat.get('gts', ''),
        nominalPower=dat.get('nominalPower'),
        energyYearEstimate=dat.get('energyYearEstimate'),
        status=dat.get('status'),
        pid=dat.get('pid'),
        uid=dat.get('uid'),
        address=address,
        profit=profit,
        energyOffset=dat.get('energyOffset'),
        gts=dat.get('gts'),
        flag=dat.get('flag')
    )
  else:
    print('Errorcode '+str(errcode))
    if json_data is not None:
        pprint(json_data)
    return {}

if (len(sys.argv) > 1):
  endpoint = str(sys.argv[1])
  if(endpoint == '--status'):
    print(getStatus())
  if(endpoint == '--energyNow'):
    print(getEnergyNow())
  if(endpoint == '--energySummary'):
    print(getEnergySummary())
  if(endpoint == '--energyTimeline'):
    print(getEnergyTimeline())
  if(endpoint == '--energyTimelineMonth'):
    print(getEnergyTimelineMonth())
  if(endpoint == '--energyTimelineYear'):
    print(getEnergyTimelineYear())
  if(endpoint == '--energyTimelineTotal'):
    print(getEnergyTimelineTotal())
  if(endpoint == '--plantInfo'):
    print(getPlantInfo())