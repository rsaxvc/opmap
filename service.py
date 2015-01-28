#!/usr/bin/env python

import web
import sqlite3


urls = (
	'/operators', 'list_operators'
)

app = web.application(urls, globals())

class list_operators:
	def GET(self):
		bbox = web.input(minLat = -90, minLon = -180, maxLat = 90, maxLon = 90)

		conn = sqlite3.connect('uls.db')
		c = conn.cursor()
		output = '[';
		rowcnt = 0
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
			''', ( bbox.minLat, bbox.maxLat, bbox.minLon, bbox.maxLon ) ):
			if( rowcnt > 0 ):
				output += ','
			output += '{"callsign":"' + row[0] + '","id":' + str(row[1]) + ',"lat":' + str(row[2]) + ',"lon":' + str(row[3]) + '}'
			rowcnt += 1
		output += ']';
		return output

if __name__ == "__main__":
    app.run()