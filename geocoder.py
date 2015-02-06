#!/usr/bin/python
from __future__ import print_function
import sys
from functools import partial

import sqlite3
import time

error = partial(print, file=sys.stderr)

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

c.execute('SELECT rowid,address,city,state,zip FROM operators WHERE rowid not in (SELECT rowid FROM operator_locations) AND state="KS"')

rows = c.fetchmany(2600)
try:
	for row in rows:

		full_address = " ".join( map(str, row[1:] ) )
		rowid = row[0]
		time.sleep(.5)

		try:
			location = geolocator.geocode(full_address)
		except exc.GeocoderQueryError:
			error( "QueryError" )
			continue
		else:
			if location:
				c.execute("INSERT INTO operator_locations VALUES(?,?,?,?,?)", ( rowid, location.latitude, location.latitude, location.longitude, location.longitude ) )

except Exception as e:
	error( e.__doc__ )
	error( e.message )

c.execute("commit")
