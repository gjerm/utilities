# Gets all chapters from the book Algoritmer og datastrukturer, merges them into one pdf

# Needs these:
# pip install beautifulsoup4
# pip install pyPdf

from bs4 import BeautifulSoup
import urllib2
import re
from pyPdf import PdfFileWriter, PdfFileReader
from StringIO import StringIO

download_list = []

page = urllib2.urlopen('http://www.iu.hio.no/~ulfu/appolonius/').read()
soup = BeautifulSoup(page, 'lxml')

content = soup.find('div', attrs={'class': 'tekst'}).find_all('div')[1].find_all('a', text=re.compile('Kapittel.*'))

def append_pdf(input,output):
    [output.addPage(input.getPage(page_num)) for page_num in range(input.numPages)]

for c in content:
	c_page = urllib2.urlopen('http://www.iu.hio.no/~ulfu/appolonius/' + c.get('href')).read()
	soup_page = BeautifulSoup(c_page, 'lxml')
	pdf_url = soup_page.find_all('a', attrs={'href': re.compile('.pdf')})
	for p in pdf_url:
		file_name = p.get('href')
		if len(file_name) == 12:
			download_list.append('http://www.iu.hio.no/~ulfu/appolonius/kap' + file_name[5] + file_name[6] + "/" + p.get('href'))
		elif len(file_name) == 11:
			download_list.append('http://www.iu.hio.no/~ulfu/appolonius/kap' + file_name[5] + "/" + p.get('href'))
		
output = PdfFileWriter()

for url in download_list:
	filename = url.split('/')[-1]
	try:
		pdf = urllib2.urlopen(url).read()
		mem_file = StringIO(pdf)
		append_pdf(PdfFileReader(mem_file), output)
		print "Got", filename
	except:
		pass

try:
	output.write(file("algs.pdf", "wb"))
	print "Assembled pdf at algs.pdf"
except Exception, e:
	print "Error ocurred!"
	print e
