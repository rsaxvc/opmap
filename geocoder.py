#!/usr/bin/python
import sqlite3

conn = sqlite3.connect('uls.db')
conn.isolation_level = None

c = conn.cursor()
c.execute("begin")

#can I do a foreign key here? Gotta look up that syntax sometime
c.execute('''CREATE VIRTUAL TABLE IF NOT EXISTS operator_locations
	USING rtree
	(rowid INT,
	minLat REAL,
	maxLat REAL,
	minLon REAL,
	maxLon REAL)
	''')

from geopy.geocoders import GoogleV3
from geopy import exc
geolocator = GoogleV3()

for row in c.execute('SELECT rowid,address,city,state,zip FROM operators WHERE rowid not in (SELECT rowid FROM operator_locations) AND city="OLATHE"'):

	full_address = " ".join( map(str, row[1:] ) )
	rowid = row[0]

	try:
		location = geolocator.geocode(full_address)
	except exc.GeocoderQueryError:
		break;
	except exc.GeocoderQuotaExceeded:
		continue;
	else:
		c.execute("INSERT INTO operator_locations VALUES(?,?,?,?,?)", ( rowid, location.latitude, location.latitude, location.longitude, location.longitude ) )

c.execute("commit")
