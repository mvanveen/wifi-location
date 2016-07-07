import datetime
import plistlib
import subprocess
import sqlite3
import random
import time

from wigle import Wigle

username = os.environ.get('WIGGLE_USERNAME')
password = os.environ.get('WIGGLE_PASSWORD')
# TODO: Makefile to compile database
# TODO: Linux *and* OS X compatibility

# TODO: cleanup
ret = subprocess.check_output(['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '--scan', '-x'])
ret = plistlib.readPlistFromString(ret)

# TODO don't hardcode db location
conn = sqlite3.connect('db/database.sql')

def insert_known_ap(conn, payload):
    for item in payload:
        result = conn.execute("select * from known_access_points where bssid = '%s'" % (item[0], ))
        result = list(result)

        if result:
            continue

        print item
        conn.execute(
            "insert into known_access_points (bssid, lat, lon, lastupdt, ssid) "
            "values (?,?,?,?,?);", item
        )
        conn.commit()

def search_lat_lon(lat, lon):
    lat_range = [lat - .1, lat + .1]
    lon_range = [lon - .1, lon + .1]
    
    #wigle = Wigle(random.choice(usernames), 'test123456').search(lat_range=lat_range, long_range=lon_range)
    wigle = Wigle(username, password).search(lat_range=lat_range, long_range=lon_range)
    payload = []
    for item in wigle:
        payload.append((
            item['netid'],
            item['trilat'],
            item['trilong'],
            item['lastupdt'],
            item['ssid']
        ))
        insert_known_ap(conn, payload)

#search_lat_lon(37.8811264, -122.28290558)

for item in ret:
   bssid = item['BSSID']
   ssid = item['SSID'].data
   rssi =  item['RSSI']
   #TODO: sql injection lol
   print bssid
   bssid = ':'.join(['{:0>2}'.format(x) for x in bssid.split(':')])
   print bssid.upper()
   result = conn.execute("select lat, lon from known_access_points where bssid = '%s';" % (bssid, ))
   result = list(result)

   conn.execute("insert into seen_access_points (bssid, time) values (?, ?)", (
       bssid,
       str(time.time())
   ))
   conn.commit()

   if not len(result):
       #continue
       #wigle = Wigle(random.choice(usernames), 'test123456').search(bssid=bssid)
       wigle = Wigle('mvanveen', 'Sho3Fee!').search(bssid=bssid)
       if not wigle:
           continue

       wigle = wigle[0]
       lat = wigle['trilat']
       lon = wigle['trilong']
       _now = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
       conn.execute("insert into known_access_points (bssid, lat, lon, lastupdt, ssid) values (?, ?, ?, ?, ?)", (
           bssid,
           lat,
           lon,
           _now,
           ssid
       ))

   else: 
       lat, lon = result[0]

   #search_lat_lon(lat, lon)
   print bssid, lat, lon, rssi
