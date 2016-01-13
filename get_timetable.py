# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from time import sleep
from urllib2 import urlopen
from collections import OrderedDict
import re

RADIO_TYPE = "XMLSpreadsheet;studentsetxmlurl;SWSCUST+StudentSet+XMLSpreadsheet"

# These are parameters that will be fetched from the page.
auto_params = ["__EVENTTARGET", "__EVENTARGUMENT", "__LASTFOCUS", "__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION", "tLinkType",
			  "tWildcard", 'bGetTimetable']

day_convert = {"Man": "mon", "Tir": "tue", "Ons": "wed", "Tor": "thu", "Fre": "fri", "Lør": "sat"}
rooms = re.compile('([A-D]\d \d{3})')
non_digits = re.compile('[\D]+')

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

	for t in tab:
		# print "Week " + str(counter)
		for c in t:
			week_info = c.find('td', {"class": "td1"})
			if week_info:
				table += week_info.getText().encode('utf-8') + "\n"
			# Exclude if header of table
			if not "tr1" in c.get('class'):
				row = c.find_all('td')
				for i in range(len(row)):
					# Remove silly whitespace
					if len(row[i].getText()) == 0:
						table += "\n"
					else:
						val = row[i].getText().encode('utf-8').strip()
						# Convert weekdays
						if i == 0:
							val = day_convert[val]
						if i == 2:
							val = val.split("-")
							table += val[0] + ";" + val[1] + ";"
							continue
						# Extract info like subject code, type of class
						elif i == 3:
							val = val[1:].split("/")
							code = val[0]
							typ = val[1]
							info = ""
							for _ in val[2:]:
								if re.findall(non_digits, _):
									info += _
							table += code + ";" + typ + ";" + info + ";"
							continue
						# Find and extract rooms
						elif i == 4:
							listed_rooms = re.findall(rooms, val)
							listed_rooms = "/".join(listed_rooms)
							val = listed_rooms
						# No need to add names of lecturers etc
						elif i == 5:
							continue

						table += val + ";"

	return table

def process_table(tab):
	
	

	for r in rows:
		l = r.split(";")
		listed_rooms = re.find_all(rooms, l[3])
		listed_rooms = "/".join(listed_rooms)


# "t" means this week
#weeks = "t"
weeks = range(1,31)

# Can be 1-3 (mon-wed), 4-6 (thu-sat) or 1-6 (mon-sat)
days = "1-6"

# "v" for spring, "h" for autumn
print get_timetable(days, weeks, "#SPLUSE0C745", "v")
# subject_codes = get_subject_codes("v")
# for k, v in subject_codes.items(): print k.encode('utf-8') + ": " + v.encode('utf-8')