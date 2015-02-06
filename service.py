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
		web.header('Content-Type', 'application/json')
		web.header('Access-Control-Allow-Origin', '*')

		bbox = web.input(minLat = -90, minLon = -180, maxLat = 90, maxLon = 90)
		tiling = web.input(tileLat = 1, tileLon = 1, tileDensity = sys.maxint )

		bbox.minLat = float( bbox.minLat )
		bbox.maxLat = float( bbox.maxLat )
		bbox.minLon = float( bbox.minLon )
		bbox.maxLon = float( bbox.maxLon )

		tiling.tileLat = int( tiling.tileLat )
		tiling.tileLon = int( tiling.tileLon )
		tiling.tileDensity = int( tiling.tileDensity )

		#extract the important parts of bbox so we can chop it up
		deltaLat = ( bbox.maxLat - bbox.minLat ) / tiling.tileLat
		deltaLon = ( bbox.maxLon - bbox.minLon ) / tiling.tileLon
		baseLat = bbox.minLat
		baseLon = bbox.minLon

		queryStart = time.time()
		conn = sqlite3.connect('uls.db')
		c = conn.cursor()
		output = '{"operators":[\n'
		first = True
		for y in xrange( tiling.tileLat ):
			for x in xrange( tiling.tileLon ):
				bbox.minLat = baseLat + deltaLat * y
				bbox.minLon = baseLon + deltaLon * x
				bbox.maxLat = baseLat + deltaLat * ( y + 1 )
				bbox.maxLon = baseLon + deltaLon * ( x + 1 )

				for row in c.execute('''
					SELECT
						callsign,rowid,minLat,minLon
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
						output += ','
					output += '{"callsign":"' + row[0] + '","id":' + str(row[1]) + ',"lat":' + str(row[2]) + ',"lon":' + str(row[3]) + '}\n'
					first = False

		output += '],"queryTime":'
		output += str( time.time() - queryStart )
		output += '}'
		return output

if __name__ == "__main__":
    app.run()
