import sqlite3
import datetime
import sys
import csv

# Parses notes from the com.example.android.notepad app, can export lines from a subset of these to a csv file

# In solid explorer, navigate to /data/data/com.example.android.notepad, put the note_pad.db next to this script

db_file = 'note_pad.db'
connection = sqlite3.connect(db_file)

cursor = connection.cursor()

if len(sys.argv) == 1:
    data = [row for row in cursor.execute("SELECT * FROM notes ORDER BY _id")]
    for row in data:
        created = datetime.datetime.fromtimestamp(row[3]/1000)
        print("ID " + str(row[0]) + " " + created.strftime("%Y-%m-%d") + " " + row[2].split('\n', 1)[0])
    print("\nChoose range of IDs to include (argument in the format X-Y)")

else:
    r = [int(v) for v in sys.argv[1].split("-")]
    data = [row for row in cursor.execute("SELECT * FROM notes WHERE _id >= ? AND _id <= ?", r)]
    print("Exporting rows:")

    for row in data:
        created = datetime.datetime.fromtimestamp(row[3]/1000)
        print("ID " + str(row[0]) + " " + created.strftime("%Y-%m-%d") + " " + row[2].split('\n', 1)[0])

    print("Remove first line of note (shown above) in export? Y/N")
    remove_title = input().lower() == 'y'
    print("Filename for CSV export?")
    filename = input() + ".csv"

    with open(filename, 'w', newline='', encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"')
        for row in data:
            created = datetime.datetime.fromtimestamp(row[3]/1000).strftime("%Y-%m-%d")
            lines = [line for index, line in enumerate(row[2].split("\n")) if line.strip() != '' and (index > 0 or not remove_title)]
            csv_rows = [[created, line.strip()] for line in lines]
            csvwriter.writerows(csv_rows)
        
    print("Written " + filename)    


connection.close()