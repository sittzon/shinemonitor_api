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

def buildRequestUrl(action: Action, salt, secret, token, devcode, plantId, pn, sn):
  if action == Action.SUMMARY:
    action_params = '&action=queryPlantCurrentData&plantid='+plantId+'&par=ENERGY_TODAY,ENERGY_MONTH,ENERGY_YEAR,ENERGY_TOTAL'#,ENERGY_PROCEEDS,ENERGY_CO2,CURRENT_TEMP,CURRENT_RADIANT,BATTERY_SOC,ENERGY_COAL,ENERGY_SO2'
  elif action == Action.TIMELINE:
    action_params = '&action=queryPlantActiveOuputPowerOneDay&plantid='+plantId+'&date=' + datetime.today().strftime('%Y-%m-%d')# + '&i18n=en_US&lang=en_US'
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

def make_request(action: Action):
  token, secret = getToken()
  salt_val = salt()
  requrl = buildRequestUrl(action, str(salt_val), secret, token, config.devcode, config.plantId, config.pn, config.sn)
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
    

def getAllData():
  # 1. Query Plant Current Data
  json_data, errcode = make_request(Action.SUMMARY)
  if errcode == 0 and json_data is not None:
    energy_today=json_data['dat'][0]['val']
    energy_month=json_data['dat'][1]['val']
    energy_year=json_data['dat'][2]['val']
    energy_total=json_data['dat'][3]['val']

    try:
      f = open("energy_summary.txt", "w")
      f.write(energy_today+'\n')
      f.write(energy_month+'\n')
      f.write(energy_year+'\n')
      f.write(energy_total)
    finally:
      f.close()

    if config.debug == 1:
      print ('Energy Today: ' + str(energy_today) +'kWh')
      print ('Energy Month: ' + str(energy_month) +'kWh')
      print ('Energy Year: ' + str(energy_year) +'kWh')
      print ('Energy Total: ' + str(energy_total) + 'kWh')
  else:
    print('Errorcode '+str(errcode))
    if json_data is not None:
        pprint(json_data)

  # 2. Query Device Data One Day Paging
  json_data, errcode = make_request(Action.ENERGY_TODAY)
  if errcode == 0 and json_data is not None:
    timestamp=json_data['dat']['row'][0]['field'][1]
    energy_now=json_data['dat']['row'][0]['field'][5]

    try:
      f = open("energy_now.txt", "w")
      f.write(timestamp+'\n')
      f.write(energy_now)
    finally:
      f.close()

    if config.debug == 1:
      print ('Timestamp: ' + str(timestamp))
      print ('Energy Now: ' + str(energy_now) + 'W')
  else:
    print('Errorcode '+str(errcode))
    if json_data is not None:
        pprint(json_data)

  # 3. Query Plant Device Designated Information
  json_data, errcode = make_request(Action.STATUS)
  if errcode == 0 and json_data is not None:
    status=json_data['dat']['device'][0]['status']

    try:
      f = open("energy_now.txt", "a")
      f.write('\n'+str(status))
    finally:
      f.close()

    if config.debug == 1:
      print ('Status: ' + str(status))
  else:
    print('Errorcode '+str(errcode))
    if json_data is not None:
        pprint(json_data)

  # 4. Query Plant Active Output Power One Day
  json_data, errcode = make_request(Action.TIMELINE)
  if errcode == 0 and json_data is not None:
    energy_over_day=json_data['dat']['outputPower']
    energy_over_day=re.sub(r'\'','\"',str(energy_over_day))

    try:
      f = open("energy_over_day.txt", "w")
      f.write(str(energy_over_day))
    finally:
      f.close()

    if config.debug == 1:
      pprint(energy_over_day)
  else:
    print('Errorcode '+str(errcode))
    if json_data is not None:
        pprint(json_data)

def getStatus():
  json_data, errcode = make_request(Action.STATUS)
  if errcode == 0 and json_data is not None:
    status=json_data['dat']['device'][0]['status']
    if (status == 0):
      status = "Online"
    else:
      status = "Offline"
    return {"Status": status}
  else:
    return {"Error": str(errcode)}

def getEnergyNow():
  json_data, errcode = make_request(Action.ENERGY_TODAY)
  if errcode == 0 and json_data is not None:
    timestamp=json_data['dat']['row'][0]['field'][1]
    energy_now=json_data['dat']['row'][0]['field'][5]
    return {
      "TimeStamp": str(timestamp),
      "Energy": float(energy_now),
      "Unit": "W"
    }
  else:
    return {"Error": str(errcode)}

def getEnergySummary():
  json_data, errcode = make_request(Action.SUMMARY)
  if errcode == 0 and json_data is not None:
    energy_today=json_data['dat'][0]['val']
    energy_month=json_data['dat'][1]['val']
    energy_year=json_data['dat'][2]['val']
    energy_total=json_data['dat'][3]['val']
    return {
      "Today": float(energy_today),
      "Month": float(energy_month),
      "Year": float(energy_year),
      "Total": float(energy_total),
      "Unit": "kWh"
    }
  else:
    return {"Error": str(errcode)}

def getEnergyTimeline():
  json_data, errcode = make_request(Action.TIMELINE)
  if errcode == 0 and json_data is not None:
    energy_over_day=json_data['dat']['outputPower']
    energy_over_day=re.sub(r'\'','"',str(energy_over_day))
    energy_over_day=re.sub(r'("val":\ )"([\d\.]+)"',r'\1\2',str(energy_over_day))
    energy_over_day=re.sub(r'"val"','"Value"',str(energy_over_day))
    energy_over_day=re.sub(r'"ts"','"TimeStamp"',str(energy_over_day))
    energy_over_day=re.sub(r'}',', "Unit": "kW"}',str(energy_over_day))
    return json.loads(energy_over_day)
  else:
    print('Errorcode '+str(errcode))
    if json_data is not None:
        pprint(json_data)

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
else:
  getAllData()