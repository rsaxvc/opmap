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

for row in c.execute('SELECT rowid,address,city,state,zip FROM operators WHERE rowid not in operator_locations.rowid'):
	print row["rowid"],row["address"],row["city"],row["state"],row["zip"]
#	c.execute("INSERT INTO operator_locations VALUES(?,?,?,?,?)", rowid, lat, lat, lon, lon )



c.execute("commit")
from geopy.geocoders import GoogleV3
geolocator = GoogleV3()
location = geolocator.geocode("5022 LANSDOWNE AVE SAINT LOUIS MO 63109")
print(location.address)
print((location.latitude, location.longitude))
print(location.raw)
