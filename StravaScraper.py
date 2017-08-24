# python StravaScraper.py

import requests
import HTMLParser

def _attr(attrs,attrname):
	for attr in attrs:
		if attr[0]==attrname: return attr[1]
	return None

class MemberParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.in_athletes=False
		self.in_member=False
		self.members=[]
		
	def handle_starttag(self,tag,attrs):
		if tag=='ul' and _attr(attrs,'class')=="list-athletes": self.in_athletes=True
		if tag=='div' and _attr(attrs,'class')=="h4 topless" and self.in_athletes: self.in_member=True
		if tag=='a' and self.in_member: self.members.append(_attr(attrs,'href'))
		
	def handle_endtag(self,tag):
		if tag=='div': self.in_member=False
		if tag=='ul': self.in_athletes=False
		
class PageParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.in_drop=False
		self.in_link=False
		self.pages=[]
		
	def handle_starttag(self,tag,attrs):
		if tag=='div' and _attr(attrs,'class')=="drop-down-menu drop-down-sm enabled": self.in_drop=True
		if tag=='ul' and _attr(attrs,'class')=="options" and self.in_drop: self.in_link=True
		if tag=='a' and self.in_link: self.pages.append(_attr(attrs,'href'))
		
	def handle_endtag(self,tag):
		if tag=='ul':
			self.in_drop=False
			self.in_link=False
		
class MonthParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.in_chart=False
		self.months=[]
		
	def handle_starttag(self,tag,attrs):
		if tag=='ul' and  _attr(attrs,'class')=="intervals": self.in_chart=True
		if tag=='a' and self.in_chart: self.months.append(_attr(attrs,'href'))
		
	def handle_endtag(self,tag):
		if tag=='ul': self.in_chart=False
		
class ActivityParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.in_name=False
		self.name=''
		self.in_h3=False
		self.in_activity=False
		self.activities=[]
		
	def handle_starttag(self,tag,attrs):
		if tag=='h2' and _attr(attrs,'class')=="h1": self.in_name=True
		if tag=='h3' and _attr(attrs,'class')=="entry-title activity-title": self.in_h3=True
		if tag=='strong' and self.in_h3: self.in_activity=True
		if tag=='a' and self.in_activity: self.activities.append(_attr(attrs,'href'))
		
	def handle_endtag(self,tag):
		if tag=='h2': self.in_name=False
		if tag=='strong': self.in_activity=False
		if tag=='h3': self.in_h3=False
		
	def handle_data(self,data):
		if self.in_name: self.name=data
		
class DataParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.in_type_link=False
		self.in_type=False
		self.data=[]
		
		self.in_details=False
		self.in_time=False
		self.in_stats=False
		self.in_data=False
		
	def handle_starttag(self,tag,attrs):
		if tag=='a' and _attr(attrs,'class')=="minimal": self.in_type_link=True
		if tag=='div' and _attr(attrs,'class')=="details": self.in_details=True
		if tag=='time' and self.in_details: self.in_time=True
		if tag=='ul' and _attr(attrs,'class')=="inline-stats section": self.in_stats=True
		if tag=='strong' and self.in_stats: self.in_data=True
		if tag=='abbr': self.in_data=False
		
	def handle_endtag(self,tag):
		if tag=='a' and self.in_type_link: self.in_type=True
		if tag=='span':
			self.in_type=False
			self.in_type_link=False
		if tag=='time':
			self.in_time=False
			self.in_details=False
		if tag=='strong': self.in_data=False
		if tag=='ul':
			self.in_stats=False
			self.in_data=False
		
	def handle_data(self,data):
		if self.in_type: self.data.append(data.replace('\n','').replace('–',''))
		if self.in_time: self.data.append(data.replace('\n','').replace(',','-'))
		if self.in_data: self.data.append(data.replace('\n','').replace(',',''))
		

global num
num=1
outfile=open('outfile.csv','w')
urls=['https://www.strava.com/clubs/125445/members?page=1','https://www.strava.com/clubs/125445/members?page=2',]
cookies={}
cookiefile=open('cookie.txt','r')
for line in cookiefile.readlines():
	name,value=line.strip().split(':',1)
	cookies[name]=value

for url in urls:
	clubPage=requests.get(url,cookies=cookies)
	memberPar=MemberParser()
	memberPar.feed(clubPage.content.decode('utf-8'))
	for member in memberPar.members:
		memberUrl="https://www.strava.com"+member+"#interval_type?chart_type=miles&interval_type=month&interval=201708&year_offset=0"
		memberPage=requests.get(memberUrl,cookies=cookies)
		pagePar=PageParser()
		pagePar.feed(memberPage.content.decode('utf-8'))
		print "#################\n# New member No."+str(num)+"...\n#################"
		num+=1
		pageUrls=[]
		pageUrls.append(memberUrl)
		pageUrls=pageUrls+pagePar.pages
		print "\n".join(pageUrls)
		for page in pageUrls:
			pageUrl=page
			monthPage=requests.get(pageUrl,cookies=cookies)
			monthPar=MonthParser()
			monthPar.feed(monthPage.content.decode('utf-8'))
			print "#############\n# New page...\n#############"
			print "\n".join(monthPar.months)
			for month in monthPar.months:
				monthUrl="https://www.strava.com"+month
				print monthUrl
				activPage=requests.get(monthUrl,cookies=cookies)
				activPar=ActivityParser()
				activPar.feed(activPage.content.decode('utf-8'))
				print "#########\n# New stage...\n#########"
				print "\n".join(activPar.activities)
				for activ in activPar.activities:
					activUrl="https://www.strava.com"+activ
					dataPage=requests.get(activUrl,cookies=cookies)
					dataPar=DataParser()
					dataPar.feed(dataPage.content.decode('utf-8'))
					outfile.write(','.join(dataPar.data[:5]))
					outfile.write('\n')
					print '    '.join(dataPar.data[:5])
					print "#####\n# New activity...\n#####"
				
outfile.close()



