import requests
from bs4 import BeautifulSoup
from time import sleep
from urllib2 import urlopen
from collections import OrderedDict

RADIO_TYPE = "XMLSpreadsheet;studentsetxmlurl;SWSCUST+StudentSet+XMLSpreadsheet"

auto_params = ["__EVENTTARGET", "__EVENTARGUMENT", "__LASTFOCUS", "__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION", "tLinkType",
			  "tWildcard", 'bGetTimetable']

def get_timetable(days, weeks, subject_code, season):
	url = "http://timeplan.uia.no/swsuia" + season + "/public/no/default.aspx"

	params = {
		'RadioType': RADIO_TYPE,
		'lbDays': days,
		'lbWeeks': ";".join(str(_) for _ in weeks),
		'dlObject': '#SPLUSE0C745'
	}

	with requests.Session() as s:
		r = s.get(url)
		soup = BeautifulSoup(r.text, 'lxml')

		for p in auto_params:
			thing = soup.find(id=p)
			if thing != None:
				val = thing.get('value')
				if val != None:
					params[p] = val
				else:
					params[p] = ""
			else:
				params[p] = ""

		sleep(1)

		if len(params['bGetTimetable']) == 0: params['bGetTimetable'] = 'Vis timeplan'

		r = s.post(url, data=params)

		soup = BeautifulSoup(r.text, 'lxml')

		print soup.prettify().encode("utf-8")
	
def get_subject_codes(season):
	results = OrderedDict()
	r = requests.get("http://timeplan.uia.no/swsuia" + season + "/public/no/default.aspx")
	soup = BeautifulSoup(r.text, 'lxml')

	l = soup.find(id='dlObject')
	if l != None:
		for o in l.find_all('option'):
			results.update({o.getText(): o.get('value')})

	return results

def convert_to_table_format():
	# Tp dp
	pass

weeks = range(1, 31)
days = "1-6"

get_timetable(days, weeks, "as", "v")
#get_subject_codes("v")