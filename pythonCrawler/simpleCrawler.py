from __future__ import division
import urllib
import HTMLParser
import re
import robotparser
import Queue as Q
import sys
import logging
from urlparse import urlparse
from pygoogle import pygoogle


def getLinks(url, htmltext):
    try:
        parsed = urlparse(url)
        rp = robotparser.RobotFileParser()
        rp.set_url(parsed.scheme + "://" + parsed.netloc + "/robots.txt")
        rp.read()
        links = []
        # Define HTML Parser

        class extractLink(HTMLParser.HTMLParser):

            def handle_starttag(self, tag, attrs):
                if(tag == "a"):
                    for attr in attrs:
                        if attr[0] == "href":
                            if rp.can_fetch("*", attr[1]):
                                if isValidUrl(attr[1]):
                                    links.append(attr[1])
                                else:
                                    if(url.endswith("/")):
                                        newurl = url + attr[1]
                                    else:
                                        newurl = url + "/" + attr[1]
                                    if (isValidUrl(newurl)):
                                        links.append(newurl)
                    
        # Create instance of HTML parser
        lParser = extractLink()
        lParser.feed(htmltext)
        return links
    except Exception as e:
        elogger.info("Failed to Parse Page : " + str(e))
    return None


def getScore(text, query):

    queryList = re.compile('\w+').findall(query)
    score = 0.0
    cnt = {}
    for word in queryList:
        cnt[word] = 0
    words = re.findall('\w+', text.lower())
    for word in words:
        if word in queryList:
            cnt[word] += 1
    for word in queryList:
        score = score + (cnt[word] / len(words))
    return score


def isValidUrl(url):
    validUrl = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        # domain...
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if validUrl.match(url):
        return True
    else:
        return False
        

FORMAT = '%(asctime)-15s %(url)s %(size)-5.2f kb %(qscore)-10s'
#logging.basicConfig(format=FORMAT)
logger = logging.getLogger('crawled')
hdlr = logging.FileHandler('crawl1.log')
ch = logging.StreamHandler()
hdlr.setLevel(logging.DEBUG)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(FORMAT)
hdlr.setFormatter(formatter)
ch.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(hdlr)
logger.addHandler(ch)

elogger = logging.getLogger('Exceptions')
ehdlr = logging.FileHandler('errors.log')
ehdlr.setLevel(logging.DEBUG)
eformatter = logging.Formatter('')
ehdlr.setFormatter(eformatter)
elogger.setLevel(logging.DEBUG)
elogger.addHandler(ehdlr)


size = 0
query = raw_input("Enter the Query: ")
noOfPages = input("Enter Number of Pages to be Crawled: ")
g = pygoogle(query)
g.pages = 1
initialList = g.get_urls()
pagesToVisit = Q.PriorityQueue()
for site in initialList:
    pagesToVisit.put((-10, site))
count = 0
while((not pagesToVisit.empty()) and count < noOfPages):
    (qscore, currentLink) = pagesToVisit.get()
    html = urllib.urlopen(currentLink)
    count = count + 1
    if(html.info().type == "text/html"):
        htmltext = html.read()
        size = size + sys.getsizeof(htmltext)
        currentScore = getScore(htmltext, query)
        d = {'url': currentLink, 'size': size/1024, 'qscore': -qscore}
        logger.info("", extra=d)
        pagelinks = getLinks(currentLink, htmltext)
        if (pagelinks is not None):
            for link in pagelinks:
                pagesToVisit.put((currentScore * -1, link))

print "Total size of downloaded Pages ::", (size / 1024), " KB"
