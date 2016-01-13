# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from time import sleep
from urllib2 import urlopen
from collections import OrderedDict

RADIO_TYPE = "XMLSpreadsheet;studentsetxmlurl;SWSCUST+StudentSet+XMLSpreadsheet"

# These are parameters that will be fetched from the page.
auto_params = ["__EVENTTARGET", "__EVENTARGUMENT", "__LASTFOCUS", "__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION", "tLinkType",
			  "tWildcard", 'bGetTimetable']

def get_timetable(days, weeks, subject_code, season):
	url = "http://timeplan.uia.no/swsuia" + season + "/public/no/default.aspx"
	html = ""

	params = {
		'RadioType': RADIO_TYPE,
		'lbDays': days,
		'lbWeeks': ";".join(str(_) for _ in weeks),
		'dlObject': subject_code
	}

	with requests.Session() as s:
		r = False
		soup = False
		params['__EVENTVALIDATION'] = False

		# Try until we get the needed parameters
		while not params['__EVENTVALIDATION']:
			r = s.get("http://timeplan.uia.no/swsuia" + season + "/public/no/login.aspx")
			soup = BeautifulSoup(r.text, 'lxml')
			params['__EVENTVALIDATION'] = soup.find(id='__EVENTVALIDATION')

		# Get parameters from the page
		for p in auto_params:
			thing = soup.find(id=p)
			if thing != None:
				val = thing.get('value')
				if val:
					params[p] = val
				else:
					params[p] = ""
			else:
				params[p] = p

		# Get the actual time table, with params as the payload
		r = s.post(url, data=params)

		soup = BeautifulSoup(r.text, 'lxml')

		return convert_to_table_format(r.text.encode('utf-8'))
		# return soup.prettify().encode("utf-8")

def get_subject_codes(season):
	results = OrderedDict()

	with requests.Session() as s:
		r = False
		soup = False
		l = False

		# Again, try until we get what we want
		while not l:
			r = s.get("http://timeplan.uia.no/swsuia" + season + "/public/no/login.aspx")
			soup = BeautifulSoup(r.text, 'lxml')
			l = soup.find(id='dlObject')

		# Make an ordered dict with subject titles and their respective codes
		if l != None:
			for o in l.find_all('option'):
				results.update({o.getText(): o.get('value')})

	return results

def convert_to_table_format(html):
	soup = BeautifulSoup(html, 'lxml')
	tab = soup.find_all('table')

	table = ""
	counter = 0

	for t in tab:
		counter += 1
		table += "Week " + str(counter) + "\n"
		# print "Week " + str(counter)
		for c in t:
			# Exclude if header of table
			if not "tr1" in c.get('class'):
				row = c.find_all('td')
				for val in row:
					# Remove silly whitespace
					if len(val.getText()) == 0:
						table += "\n"
					else:
						table += val.getText().encode('utf-8').strip() + ";"
	return table

# A list of weeks to return (should start at 1 and not skip any weeks for now)
weeks = range(1, 31)

# Can be 1-3 (mon-wed), 4-6 (thu-sat) or 1-6 (mon-sat)
days = "1-6"

# "v" for spring, "h" for autumn
print get_timetable(days, weeks, "#SPLUSE0C745", "v")
#print get_subject_codes("v")