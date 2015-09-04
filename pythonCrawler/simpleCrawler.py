import urllib
import HTMLParser



def getLinks(url):
	links = []
	print "--->" + url
	#Define HTML Parser
	class extractLink(HTMLParser.HTMLParser):
        
	    def handle_starttag(self, tag, attrs):
	        if(tag == "a"):
	        	for attr in attrs:
	        		if attr[0] == "href":
	        			if "http" in attr[1]:
	        				links.append(attr[1])
	        			else:
	        				links.append(url + "/" + attr[1])

	#Create instance of HTML parser
	lParser = extractLink()
	lParser.feed(urllib.urlopen(url).read())
	return links 

def isRelevant(url,query):
	text = urllib.urlopen(url).read()
	print text
	if (query in text):
		return True
	else:
		return False

    
pagesToVisit = ["http://cis.poly.edu/cs6913"]

while(pagesToVisit):
	currentLink = pagesToVisit.pop(0)
	print currentLink
	html = urllib.urlopen(currentLink)
	if(html.info().type == "text/html"):
		pagelinks = getLinks(currentLink)
		pagesToVisit.extend(pagelinks)

