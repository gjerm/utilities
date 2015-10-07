# Gets all chapters from the book Algoritmer og datastrukturer, merges them into one pdf (algs.pdf)

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

def get_book():
	for c in content:
		dl_this = []
		c_page = urllib2.urlopen('http://www.iu.hio.no/~ulfu/appolonius/' + c.get('href')).read()
		soup_page = BeautifulSoup(c_page, 'lxml')
		pdf_url = soup_page.find_all('a', attrs={'href': re.compile('.pdf')})
		for p in pdf_url:
			file_name = p.get('href')
			if len(file_name) == 12:
				dl_this.append('http://www.iu.hio.no/~ulfu/appolonius/kap' + file_name[5] + file_name[6] + "/" + p.get('href'))
			elif len(file_name) == 11:
				dl_this.append('http://www.iu.hio.no/~ulfu/appolonius/kap' + file_name[5] + "/" + p.get('href'))
		download_list.append(dl_this)


def get_chapters():
	for url in download_list:
		output = PdfFileWriter()
		errored = False
		if url:
			filename = url[0].split('/')[-1]
			p = re.compile('(?<=kap)\d{1,3}')
			chap = p.search(filename).group()
			chap = chap[:-1]
			print "Doing chapter", chap
			for u in url:
				try: 
					pdf = urllib2.urlopen(u).read()
					mem_file = StringIO(pdf)
					append_pdf(PdfFileReader(mem_file), output)
				except Exception, e:
					print "Error for chapter " + chap + ": " + str(e)
					errored = True
					pass
			try:
				if not errored: 
					output.write(file("algs-kap" + chap + ".pdf", "wb"))
					print "Assembled pdf at algs-"+ chap + ".pdf"
				else:
					print "Couldn't get chapter, not assembled"

			except Exception, e:
				print "Error ocurred!"
				print e

def get_full_book_pdf():
	output = PdfFileWriter()
	for url in download_list:
		if url:
			for u in url:
				try: 
					pdf = urllib2.urlopen(u).read()
					mem_file = StringIO(pdf)
					append_pdf(PdfFileReader(mem_file), output)
				except Exception, e:
					print "Error for chapter; " + str(e)
					pass
	try:
		output.write(file("algs-full.pdf", "wb"))
		print "Assembled pdf at algs-full.pdf\n"

	except Exception, e:
			print "Error ocurred!"
			print e



get_book()
get_chapters()
#get_full_book_pdf()