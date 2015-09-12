from __future__ import division
import urllib
import HTMLParser
import re
import robotparser
import Queue as Q
from urlparse import urlparse
from pygoogle import pygoogle



def getLinks(url, html):
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
                            else:
                                print "Robot.txt disallows crawling url"

        # Create instance of HTML parser
        lParser = extractLink()
        lParser.feed(html.read())
        return links
    except Exception as e:
        print "Failed to Parse Page : " + str(e)
    return None


def getScore(html, query):
    text = html.read()
    score = 0.0
    cnt = {}
    for word in query:
        cnt[word] = 0
    words = re.findall('\w+', text.lower())
    for word in words:
        if word in query:
            cnt[word] += 1
    for word in query:
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


query = raw_input("Enter the Query: ")
noOfPages = input("Enter Number of Pages to be Crawled: ")
g = pygoogle(query)
g.pages = 1
pagesToVisit = g.get_urls()
count = 0
while(pagesToVisit and count < noOfPages):
    currentLink = pagesToVisit.pop(0)
    print currentLink
    count = count + 1
    html = urllib.urlopen(currentLink)
    if(html.info().type == "text/html"):
        pagelinks = getLinks(currentLink, html)
        if(pagelinks is not None):
            pagesToVisit.extend(pagelinks)
