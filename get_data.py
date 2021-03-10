#!/usr/bin/python3
import urllib, hashlib
from urllib.request import urlopen
from pprint import pprint
import requests
import json
import time as time_             #make sure we don't override time
from datetime import datetime
import config
import re

def salt():
    return int(round(time_.time() * 1000))

def getToken(salt):
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
  token=r.json()['dat']['token']
  secret=r.json()['dat']['secret']
  expire=r.json()['dat']['expire']
  return token, secret, expire

#action = :
#queryPlantCurrentData - Returns json summary of energy generated
#queryPlantActiveOuputPowerOneDay - (Misspelled in API) Returns json data used in shinemonitor for displaying today graph over generated energy
#queryDeviceDataOneDayPaging - Returns various json data, ex. energy generated now
#queryPlantDeviceDesignatedInformation - Return for example offline/online status of inverter
def buildRequestUrl(action, salt, secret, token, devcode, plantId, pn, sn):
  if action == 'queryPlantCurrentData':
    action='&action=queryPlantCurrentData&plantid='+plantId+'&par=ENERGY_TODAY,ENERGY_MONTH,ENERGY_YEAR,ENERGY_TOTAL,ENERGY_PROCEEDS,ENERGY_CO2,CURRENT_TEMP,CURRENT_RADIANT,BATTERY_SOC,ENERGY_COAL,ENERGY_SO2'
  elif action == 'queryPlantActiveOuputPowerOneDay':
    action='&action=queryPlantActiveOuputPowerOneDay&plantid='+plantId+'&date=' + datetime.today().strftime('%Y-%m-%d') + '&i18n=en_US&lang=en_US'
  elif action == 'queryDeviceDataOneDayPaging':
    action='&action=queryDeviceDataOneDayPaging&devaddr=1&pn='+pn+'&devcode='+devcode+'&sn='+sn+'&date='+datetime.today().strftime('%Y-%m-%d')+'&page=0&pagesize=50&i18n=en_US&lang=en_US'
  elif action == 'queryPlantDeviceDesignatedInformation':
    action='&action=queryPlantDeviceDesignatedInformation&plantid='+plantId+'&devtype=512&i18n=en_US&parameter=energy_today,energy_total&i18n=en_US&lang=en_US'

  reqaction= str(salt) + secret + token + action
  req_sign=hashlib.sha1()
  req_sign.update(reqaction.encode('utf-8'))
  sign = str(req_sign.hexdigest())
  requrl= baseURL + '?sign='+ sign + '&salt=' + str(salt) + '&token=' + token + action
  return requrl

baseURL = 'http://web.shinemonitor.com/public/'

#Use token if exists
token, secret, expire = '','',''
try:
  f = open("token", "r")
  if config.debug == 1:
    print("Using tokenfile credentials")
  token = f.readline().strip()
  secret= f.readline().strip()
  expire= f.readline().strip()
  #Try using token
  requrl = buildRequestUrl('queryPlantDeviceDesignatedInformation', str(salt), secret, token, config.devcode, config.plantId, config.pn, config.sn)
  r = requests.get(requrl)
  errcode = r.json()['err']
  if errcode != 0:
    print("Token invalid")
    raise error
except:
  if config.debug == 1:
    print("Logging in using credentials")
  token, secret, expire = getToken(salt())
  f = open("token", "w")
  f.write(token+'\n')
  f.write(secret+'\n')
  f.write(str(expire))
finally:
  f.close

#Get data
requrl = buildRequestUrl('queryPlantCurrentData', str(salt), secret, token, config.devcode, config.plantId, config.pn, config.sn)
if config.debug == 1:
  print (requrl)
r = requests.get(requrl)

errcode = r.json()['err']
if errcode == 0:
  energy_today=r.json()['dat'][0]['val']
  energy_month=r.json()['dat'][1]['val']
  energy_year=r.json()['dat'][2]['val']
  energy_total=r.json()['dat'][3]['val']

  try:
    f = open("energy_summary.txt", "w")
    f.write(energy_today+'\n')
    f.write(energy_month+'\n')
    f.write(energy_year+'\n')
    f.write(energy_total)
  finally:
    f.close

  if config.debug == 1:
    print ('Energy Today: ' + str(energy_today) +'kWh')
    print ('Energy Month: ' + str(energy_month) +'kWh')
    print ('Energy Year: ' + str(energy_year) +'kWh')
    print ('Energy Total: ' + str(energy_total) + 'kWh')
else:
  print('Errorcode '+str(errcode))
  pprint(r.json())

requrl = buildRequestUrl('queryDeviceDataOneDayPaging', str(salt), secret, token, config.devcode, config.plantId, config.pn, config.sn)
if config.debug == 1:
  print (requrl)
r = requests.get(requrl)

errcode = r.json()['err']
if errcode == 0:
  timestamp=r.json()['dat']['row'][0]['field'][1]
  energy_now=r.json()['dat']['row'][0]['field'][5]

  try:
    f = open("energy_now.txt", "w")
    f.write(timestamp+'\n')
    f.write(energy_now)
  finally:
    f.close

  if config.debug == 1:
    print ('Timestamp: ' + str(timestamp))
    print ('Energy Now: ' + str(energy_now) + 'W')
else:
  print('Errorcode '+str(errcode))
  pprint(r.json())


requrl = buildRequestUrl('queryPlantDeviceDesignatedInformation', str(salt), secret, token, config.devcode, config.plantId, config.pn, config.sn)
if config.debug == 1:
  print (requrl)
r = requests.get(requrl)

errcode = r.json()['err']
if errcode == 0:
  status=r.json()['dat']['device'][0]['status']

  try:
    f = open("energy_now.txt", "a")
    f.write('\n'+str(status))
  finally:
    f.close

  if config.debug == 1:
    print ('Status: ' + str(status))
else:
  print('Errorcode '+str(errcode))
  pprint(r.json())

requrl = buildRequestUrl('queryPlantActiveOuputPowerOneDay', str(salt), secret, token, config.devcode, config.plantId, config.pn, config.sn)
if config.debug == 1:
  print (requrl)
r = requests.get(requrl)

errcode = r.json()['err']
if errcode == 0:
  energy_over_day=r.json()['dat']['outputPower']
  energy_over_day=re.sub(r'\'','\"',str(energy_over_day))

  try:
    f = open("energy_over_day.txt", "w")
    f.write(str(energy_over_day))
  finally:
    f.close

  if config.debug == 1:
    pprint(energy_over_day)
else:
  print('Errorcode '+str(errcode))
  pprint(r.json())