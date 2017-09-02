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
		if tag=='a' and self.in_desc: self.EANurls.append([_attr(attrs,'href'),_attr(attrs,'title')])
		if tag=='div' and _attr(attrs,'id')=='pager': self.in_result=False
	def handle_endtag(self,tag):
		if tag=='span': self.in_desc=False
	def handle_data(self,data):
		pass

class EANParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.EAN_num=[]
		self.in_attr=False
		self.in_label=False
		self.in_EAN=False
		
	def handle_starttag(self,tag,attrs):
		if tag=='div' and _attr(attrs,'class')=='itemAttr': self.in_attr=True
		if tag=='td' and _attr(attrs,'class')=='attrLabels' and self.in_attr: self.in_label=True
		if tag=='div' and _attr(attrs,'id')=='desc_wrapper_ctr':
			self.in_label=False
			self.in_attr=False
			self.in_EAN=False
		
	def handle_endtag(self,tag):
		if tag=='span': self.in_EAN=False
		
	def handle_data(self,data):
		if self.in_label and ('EAN:' in data):
			self.in_EAN=True
		if self.in_EAN:
			self.EAN_num.append(data.strip())

url='http://stores.ebay.de/Spar-King-Shop/_i.html'
params={"rt":"nc","_ipg":192}

outfile=open('EAN_Ebay.csv','w')

for i in range(1):
	params['_pgn']=i+1
	page=requests.get(url,params=params)
	print("########################\n# We have scraped page "+str(i+1)+"...\n########################")
	ebaypar=EbayParser()
	ebaypar.feed(page.content.decode('utf-8'))
	print(str(ebaypar.EANurls))
	for EANurl in ebaypar.EANurls:
		EANpage=requests.get(EANurl[0])
		EANpar=EANParser()
		EANpar.feed(EANpage.content.decode('utf-8'))
		print(EANurl[0]+'---------->'+EANurl[1])
		outfile.write(EANurl[1]+",'"+EANpar.EAN_num[3]+"\n")
	
outfile.close()