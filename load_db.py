import sqlite3
import csv

with open('EN.dat','rb') as csvfile:
	spamreader = csv.reader(csvfile, delimiter='|')
	for row in spamreader:
		callsign = row[4]
		fullname = row[7]
		firstname = row[8]
		middleinitial = row[9]
		lastname = row[10]
		address = row[15]
		city = row[16]
		state = row[17]
		zip = row[18]
#		print ', '.join(row)
		print address
