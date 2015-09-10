from __future__ import division
import urllib
import HTMLParser
import re
import robotparser
from urlparse import urlparse
from pygoogle import pygoogle


def getScore(html,query):
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
		score = score + (cnt[word]/len(words)) 
	return score
	
html = urllib.urlopen("http://en.wikipedia.org/wiki/Jeans")
query = ["blue" , "jeans"] 
print getScore(html,query)