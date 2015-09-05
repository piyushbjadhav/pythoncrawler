import urllib
import HTMLParser
import re
from pygoogle import pygoogle


def getLinks(url):
	try:
		links = []
		print "--->" + url
		#Define HTML Parser
		class extractLink(HTMLParser.HTMLParser):
	        
		    def handle_starttag(self, tag, attrs):
		        if(tag == "a"):
		        	for attr in attrs:
		        		if attr[0] == "href":
		        			if isValidUrl(attr[1]):
		        				links.append(attr[1])
		        			else:
		        				if(url.endswith("/")):
		        					newurl = url + attr[1]
		        				else:
		        					newurl = url + "/" + attr[1]
		        				if (isValidUrl(newurl)):
		        					links.append(newurl)

		#Create instance of HTML parser
		lParser = extractLink()
		lParser.feed(urllib.urlopen(url).read())
		return links 
	except Exception as e:
		"Failed to Parse Page : "+str(e)
    	return None

def isRelevant(url,query):
	text = urllib.urlopen(url).read()
	print text
	if (query in text):
		return True
	else:
		return False

def isValidUrl(url):
	validUrl = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

	if validUrl.match(url):
		return True
	else:
		return False



query = raw_input("Enter the Query: ")
noOfPages = input("Enter Number of Pages to be Crawled: ")
g = pygoogle(query)
g.pages = 1
pagesToVisit = g.get_urls()
count = 0
while(pagesToVisit or count < noOfPages ):
	currentLink = pagesToVisit.pop(0)
	print currentLink
	count = count + 1
	html = urllib.urlopen(currentLink)
	if(html.info().type == "text/html"):
		pagelinks = getLinks(currentLink)
		if(pagelinks is not None):
			pagesToVisit.extend(pagelinks)


