from __future__ import division
from threading import Thread
import urllib
import HTMLParser
import re
import robotparser
import Queue as Q
import sys
import logging
from urlparse import urlparse
from pygoogle import pygoogle
from urlparse import urlsplit, urlunsplit, parse_qsl ,urljoin
from urllib import urlencode,FancyURLopener
import urlnorm
from math import log,sqrt
import os
import time


def get_score(document,query):
    query_terms = re.findall("\w+", query.lower())
    score = 0.0
    mag = 0.0
    for term in query_terms:
        idf = get_idf(term)
        doc_tfid = termFrequency(term,document) * idf
        score += doc_tfid * idf
        mag += sqrt(idf*idf) + sqrt(doc_tfid * doc_tfid)
    return (score/mag)*-1

def get_idf(term):
    if term in wordlist:
        no_of_occurences = wordlist[term]
    else:
        no_of_occurences = 100
    idf = 1.0 + log((1229245740 / no_of_occurences))
    return idf 

def termFrequency(term, document):
    normalizeDocument = document.lower().split()
    return normalizeDocument.count(term.lower()) / float(len(normalizeDocument))


#normalizes url
def canonizeurl(url):                      
    split = urlsplit(urlnorm.norm(url))
    path = split[2].split(' ')[0]
    while path.startswith('/..'):
        path = path[3:]
    while path.endswith('%20'):
        path = path[:-3]
    #qs = urlencode(sorted(parse_qsl(split.query)))
    qs = ""
    return urlunsplit((split.scheme, split.netloc, path, qs, ''))

#returns parsed hyperlinks
def getLinks(url, htmltext):
    try:
        vis = set()
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
                            extracted_url = attr[1]
                            if(not url.endswith("/")):
                                extracted_url = extracted_url + '/'
                            joined_url = urljoin(parsed.scheme + "://" + parsed.netloc + "/",extracted_url)
                            if (isValidUrl(joined_url)):
                                canurl =  canonizeurl(joined_url)
                                if rp.can_fetch("*", canurl):
                                    if(('javascript:void(0)' not in canurl) and (canurl not in vis)):
                                            #print canurl
                                            vis.add(canurl)
                                            links.append(canurl)
                                

        # Create instance of HTML parser
        lParser = extractLink()
        lParser.feed(htmltext)
        return links
    except Exception as e:
        elogger.info("Failed to Parse Page : " + str(e))
    return None

#gets score
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

#checks if url is valid
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
#worker threar, fethches from queue and processes it
def worker():
    global count
    global size
    global completecount
    global visitedPages

    class MyOpener(FancyURLopener):
        version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11)'
        
    try:
        while (not pagesToVisit.empty() and count < noOfPages):
            (qscore, currentLink ) = pagesToVisit.get()
            if(currentLink in visitedPages):
                continue
            visitedPages.add(currentLink)
            myopener = MyOpener()

            html = myopener.open(currentLink)
            code = html.getcode()
            count = count + 1
            if(html.info().type == "text/html"):
                htmltext = html.read()
                size = size + sys.getsizeof(htmltext)
                currentScore = get_score(htmltext, query)
                d = {'url': currentLink, 'size': size/1024, 'qscore': -qscore , 'code' : code ,'ascore':-currentScore}
                logger.info("", extra=d)
                parsed = urlparse(currentLink)
                path = parsed.path
                if path == "":
                    path = 'index.html'
                storagepath = path.split('/')[-1]
                if storagepath == "":
                    storagepath = 'default.html'
                if not os.path.exists('pages/'+parsed.netloc):
                    os.makedirs('pages/'+parsed.netloc)
                loc = 'pages/' + parsed.netloc + '/' + storagepath + '.html'
                with open(loc, 'wb') as f:
                    f.write(htmltext)
                pagelinks = getLinks(currentLink, htmltext)
                if ((pagelinks is not None) and count < noOfPages):
                    for link in pagelinks:
                        pagesToVisit.put((currentScore , link))
            pagesToVisit.task_done()
        completecount += 1
        if(completecount == 8):
            while(not pagesToVisit.empty()):
                pagesToVisit.get()
                pagesToVisit.task_done()
    except Exception as e:
        elogger.info("Problem Fetching URL : " + str(e))



FORMAT = '%(asctime)-15s %(code)-3s %(url)s %(size)-5.2f kb %(qscore)-.4f %(ascore)-.4f'
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

if not os.path.exists('pages'):
    os.makedirs('pages')

visitedPages = set()
completecount = 0
size = 0
wordlist = {}

print "Initializing Scorer ...."
with open('wikipedia_wordfreq.txt','r') as f:
    for line in f:
        entry = line.split("\t")
        term = entry[0]
        freq = entry[1]
        wordlist[term] = int(freq)
 
print "Initialized."

query = raw_input("Enter the Query: ")
noOfPages = input("Enter Number of Pages to be Crawled: ")
start_time = time.time()
g = pygoogle(query)
g.pages = 1
initialList = g.get_urls()
pagesToVisit = Q.PriorityQueue()
for site in initialList:
    pagesToVisit.put((-10, site))
count = 0

for i in range(16):
     t = Thread(target=worker)
     t.daemon = True
     t.start()

while(count != noOfPages):
    pass
with open('crawl1.log','a' ) as f:
    f.write("User Query                     :: %s \n" % query )
    f.write("Number of Pages Crawled        :: %s \n" % count )
    f.write("Total size of downloaded Pages :: %.2f KB\n" % (size / 1024) )
    f.write("Total time                     :: %s seconds" % (time.time() - start_time) )
sys.exit(1)
