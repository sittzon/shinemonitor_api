#!/usr/bin/python3
import urllib, hashlib
from urllib.request import urlopen
from pprint import pprint
import requests
import json
import time as time_             #make sure we don't override time
from datetime import datetime
import config

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

#queryPlantActiveOuputPowerOneDay - Returns json data used in shinemonitor for displaying today graph over generated wattage
#queryPlantDeviceStatus - Returns json status of inverter 0=OK
#queryPlantCurrentData - Returns json summary of energy generated
def buildRequestUrl(action, salt, secret, token, devcode, plantId, pn, sn):
  if action == 'queryPlantCurrentData':
    action='&action=queryPlantCurrentData&plantid='+plantId+'&par=ENERGY_TODAY,ENERGY_MONTH,ENERGY_YEAR,ENERGY_TOTAL,ENERGY_PROCEEDS,ENERGY_CO2,CURRENT_TEMP,CURRENT_RADIANT,BATTERY_SOC,ENERGY_COAL,ENERGY_SO2'
  elif action == 'queryPlantActiveOuputPowerOneDay':
    action='&action=queryPlantActiveOuputPowerOneDay&plantid='+plantId+'&date=' + datetime.today().strftime('%Y-%m-%d') + '&i18n=en_US&lang=en_US'
  elif action == 'queryDeviceRealLastData':
    action='&action=queryDeviceRealLastData&devaddr=1&pn'+pn+'&devcode='+devcode+'&sn='+sn+'&date='+datetime.today().strftime('%Y-%m-%d')+'&i18n=en_US&lang=en_US'
  elif action == 'queryDeviceDataOneDayPaging':
    action='&action=queryDeviceDataOneDayPaging&devaddr=1&pn='+pn+'&devcode='+devcode+'&sn='+sn+'&date='+datetime.today().strftime('%Y-%m-%d')+'&page=0&pagesize=50&i18n=en_US&lang=en_US'

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
  print("Using tokenfile credentials")
  token = f.readline()
  secret= f.readline()
  expire= f.readline()
  f.close
except:
  print("Tokenfile not found, logging in using credentials")
  token, secret, expire = getToken(salt())
  #Store token info in file
  f = open("token", "w")
  f.write(token+'\n')
  f.write(secret+'\n')
  f.write(str(expire))
  f.close
finally:
  f.close

#Get data
requrl = buildRequestUrl('queryPlantCurrentData', salt, secret, token, config.devcode, config.plantId, config.pn, config.sn)
print (requrl)
r = requests.get(requrl)
#pprint(r.json())

errcode = r.json()['err']
if errcode == 0:
  total_energy=r.json()['dat'][3]['val']
  today_energy=r.json()['dat'][0]['val']
  if config.debug == 1:
    print ('Total energy: ' + str(total_energy) + 'kWh')
    print ('Today energy: ' + str(today_energy) +'kWh')
else:
  print('Errorcode '+str(errcode))

requrl = buildRequestUrl('queryDeviceDataOneDayPaging', salt, secret, token, config.devcode, config.plantId, config.pn, config.sn)
print (requrl)
r = requests.get(requrl)

errcode = r.json()['err']
if errcode == 0:
  timestamp=r.json()['dat']['row'][0]['field'][1]
  energy_now=r.json()['dat']['row'][0]['field'][5]
  if config.debug == 1:
    print ('Timestamp: ' + str(timestamp))
    print ('Energy Now: ' + str(energy_now) + 'W')
else:
  print('Errorcode '+str(errcode))