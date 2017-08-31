# python Ebay.py
# http://stores.ebay.de/Spar-King-Shop/_i.html?rt=nc&_pgn=2&_ipg=192

import requests
from html.parser import HTMLParser

def _attr(attrs,attrname):
	for attr in attrs:
		if attr[0]==attrname: return attr[1]
	return None

class EbayParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.EANurls=[]
		self.in_result=False
		self.in_desc=False
		
	def handle_starttag(self,tag,attrs):
		if tag=='div' and _attr(attrs,'id')=='result-set': self.in_result=True
		if tag=='div' and _attr(attrs,'class')=='desc' and self.in_result: self.in_desc=True
		if tag=='a' and self.in_desc: self.EANurls.append(_attr(attrs,'href'))
	def hanndle_endtag(self,tag):
		if tag=='span': self.in_desc=False
		if tag=='div' and _attr(attrs,'id')=='pager': self.in_result=False
	def handle_data(self,data):
		pass

class EANParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.in_block=False
		self.in_EAN=False
		self.EAN=''
		
	def handle_starttag(self,tag,attrs):
		if tag=='td' and _attr(attrs,'class')=='attrLabels': self.in_block=True
	def hanndle_endtag(self,tag):
		if tag=='span': self.in_EAN=False
	def handle_data(self,data):
		if self.in_block and ('EAN:' in data): self.in_EAN=True
		if self.in_EAN: self.EAN_num=data.strip()

url='http://stores.ebay.de/Spar-King-Shop/_i.html'
params={"rt":"nc","_ipg":192}

outfile=open('EAN_Ebay.csv','w')

for i in range(2):
	params['_pgn']=i+1
	page=requests.get(url,params=params)
	print("########################\n# We have scraped page "+str(i+1)+"...\n########################")
	ebaypar=EbayParser()
	ebaypar.feed(page.content.decode('utf-8'))
	for EANurl in ebaypar.EANurls:
		EANpage=requests.get(EANurl)
		EANpar=EANParser()
		EANpar.feed(EANpage.content.decode('utf-8'))
		print(EANurl)
		outfile.write(EANpar.EAN_num+'\n')
	
outfile.close()
