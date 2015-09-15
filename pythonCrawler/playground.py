from __future__ import division
import urllib
import HTMLParser
import re
import robotparser
import Queue as Q
from urlparse import urlparse
from pygoogle import pygoogle

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
                    print "HyperLink Found"
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
        print links
        return links
    except Exception as e:
        print "Failed to Parse Page : " + str(e)
    return None

url = "http://www.cars.com"
html = urllib.urlopen(url)
print getLinks(url,html)