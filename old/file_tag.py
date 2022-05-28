# Utility for adding tags to files and ability to search by tags. Non-functional at the moment.

import re
import sqlite3 as sql
import os

path = os.environ['APPDATA'] + "\\Tagfile"
if not os.path.exists(path): os.makedirs(path)
db_name = path + "\\taggedfiles.db"
db_con = False

class tagged_file():
	def __init__(self, file_path, tags):
		self.tags = tags
		self.file_path = file_path

	def tags_as_string(self):
		return list_to_string(self.tags)

	def add_tags(self, tags):
		tags = string_to_list(tags)
		if tags:
			for t in tags:
				self.tags.append(t)
		else:
			print "No tags to add!"

	def remove_tag(self, tag):
		try:
			del self.tags[self.tags.index(tag)]
		except:
			print "Tag " + tag + " not found, won't remove."

	def remove_all_tags(self):
		self.tags = []

	def has_tag(self, tag):
		if tag in self.tags: return True
		else: return False

	def search(self, term):
		match = []
		for s in self.tags:
			if term in s:
				match.append(s)
		return match

	def set_tags_from_str(self, string):
		self.tags = string_to_list(string)

	def add_to_db(self):
		if db_con:
			with db_con:
				cur = db_con.cursor()
				cur.execute("INSERT INTO Files VALUES(\'" + self.file_path + "\', \'" + self.tags_as_string() + "\')")

	def update_tags(self):
		if db_con:
			with db_con:
				cur = db_con.cursor()
				cur.execute("UPDATE Files SET Tags=\'" + self.tags_as_string() + "\' WHERE Filepath=\'" + self.file_path + "\'")


def list_to_string(l):
	return ', '.join(l)

def string_to_list(s):
	return re.findall(re.compile('[^\s,]+\s*[^\s,]+'), s)

def db_connect():
    global db_con
    try:
        db_con = sql.connect(db_name)
        with db_con:
            cur = db_con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS Files(Filepath TEXT, Tags TEXT)")
        print "-- Connected to database"
        return True
    except sql.Error, e:
        print "Error %s" % e.args[0]
        return False

def db_disconnect():
    global db_con
    if db_con:
        try:
            db_con.close()
            print "-- Disconnected from database"
            db_con = False
            return True
        except:
            print "-- Error disconnecting from database"
            return False
    else:
        print "Database is not connected"


def db_load_files():
	files = []
	if db_con:
		with db_con:
			cur = db_con.cursor()
			cur.execute('SELECT * FROM Files')
			files = cur.fetchall()
	return [tagged_file(f[0], string_to_list(f[1])) for f in files]

def db_clear():
    if not db_con: db_connect()
    with db_con:
        cur = db_con.cursor()
        cur.execute("DELETE FROM Files")
        cur.execute("VACUUM")
    print "-- Cleared table Files"
    return True

rick = tagged_file("C:\Users\dfood\Music\Interstellar (Original Motion Picture Soundtrack)\\05 Stay.flac", ["entertainment", "music"])
skool = tagged_file("C:\Users\dfood\Downloads\icmp-ethereal-trace-2.pcap", ["school", "tech  \n ", "wireshark"])

print db_name
db_connect()
db_clear()
search = "e"

rick.add_tags("test1, test2")

rick.add_to_db()
skool.add_to_db()


files = db_load_files()
for f in files: print list_to_string(f.tags)

print "Files with tags that match the search '" + search + "':"
for f in files:
	m = f.search(search)
	if m:
		print "Found tags '" + list_to_string(m) + "' for " + f.file_path

search = "scho"
print "\nFiles with tags that match the search '" + search + "':"
for f in files:
	m = f.search(search)
	if m:
		print "Found tags '" + list_to_string(m) + "' for " + f.file_path
db_disconnect()