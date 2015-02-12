#!/usr/bin/env python

import web
import sqlite3
import time
import sys

urls = (
	'/operators', 'list_operators'
)

app = web.application(urls, globals())

class list_operators:
	def GET(self):
		web.header('Access-Control-Allow-Origin', '*')
		web.header('Content-Type', 'application/json')
		web.header('Transfer-Encoding', 'chunked')

		bbox = web.input(minLat = -90, minLon = -180, maxLat = 90, maxLon = 90)
		tiling = web.input(tileLat = 1, tileLon = 1, tileDensity = sys.maxint )

		bbox.minLat = float( bbox.minLat )
		bbox.maxLat = float( bbox.maxLat )
		bbox.minLon = float( bbox.minLon )
		bbox.maxLon = float( bbox.maxLon )

		tiling.tileLat = int( tiling.tileLat )
		tiling.tileLon = int( tiling.tileLon )
		tiling.tileDensity = int( tiling.tileDensity )
		if tiling.tileLat < 1:
			tiling.tileLat = 1
		if tiling.tileLon < 1:
			tiling.tileLon = 1

		#extract the important parts of bbox so we can chop it up
		deltaLat = ( bbox.maxLat - bbox.minLat ) / tiling.tileLat
		deltaLon = ( bbox.maxLon - bbox.minLon ) / tiling.tileLon
		baseLat = bbox.minLat
		baseLon = bbox.minLon

		queryStart = time.time()
		conn = sqlite3.connect('uls.db')
		conn.isolation_level = None
		conn.row_factory = sqlite3.Row
		c = conn.cursor()

		c.execute('PRAGMA mmap_size=' + str(1024*1024*256) + ';' )
		c.execute('PRAGMA cache_size=-' + str(1024*256) +';' )
		c.execute('PRAGMA query_only=1;' )
		c.execute('BEGIN')

		yield '{"operators":['
		first = True
		for y in xrange( tiling.tileLat ):
			for x in xrange( tiling.tileLon ):
				bbox.minLat = baseLat + deltaLat * y
				bbox.minLon = baseLon + deltaLon * x
				bbox.maxLat = baseLat + deltaLat * ( y + 1 )
				bbox.maxLon = baseLon + deltaLon * ( x + 1 )

				for row in c.execute('''
					SELECT
						callsign,fname,lname,address,city,state,zip,rowid,minLat,minLon
					FROM
						operator_locations,operators
					WHERE
						operators.rowid = operator_locations.rowid
					AND
						operator_locations.minLat > ?
					AND
						operator_locations.minLat < ?
					AND
						operator_locations.minLon > ?
					AND
						operator_locations.minLon < ?
					LIMIT
						?
					''', ( bbox.minLat, bbox.maxLat, bbox.minLon, bbox.maxLon, tiling.tileDensity ) ):
					if( first == False ):
						yield ','
					yield ('{' +
						'"callsign":"' + row["callsign"]    + '"' +
							',' +
						'"id":'        + str(row["rowid"])  +
							',' +
						'"firstName":"'+ row["fname"]       + '"' +
							',' +
						'"lastName":"' + row["lname"]       + '"' +
							',' +
						'"address":"'  + row["address"]     + '"' +
							',' +
						'"city":"'     + row["city"]        + '"' +
							',' +
						'"state":"'    + row["state"]       + '"' +
							',' +
						'"zip":'       + str(row["zip"])    +
							',' +
						'"lat":'       + str(row["minLat"]) +
							',' +
						'"lon":'       + str(row["minLon"]) +
						'}\n')
					first = False

		c.execute('COMMIT')
		yield '],"queryTime":' + str( time.time() - queryStart ) + '\n}'

if __name__ == "__main__":
    app.run()
