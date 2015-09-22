from math import log,sqrt
import re

def get_score(document,query):
	query_terms = re.findall("\w+", query.lower())
	score = 0.0
	mag = 0.0
	for term in query_terms:
		idf = get_idf(term)
		doc_tfid = termFrequency(term,document) * idf
		score += doc_tfid * idf
		mag += sqrt(idf*idf) + sqrt(doc_tfid * doc_tfid)
	return score/mag

def get_idf(term):
	if term in wordlist:
		print term," present"
		no_of_occurences = wordlist[term]
	else:
		print term," absent"
		no_of_occurences = 100
	idf = 1.0 + log((1229245740 / no_of_occurences))
	return idf 

def termFrequency(term, document):
    normalizeDocument = document.lower().split()
    return normalizeDocument.count(term.lower()) / float(len(normalizeDocument))
wordlist ={}
wordlist['4540'] = 1
print "getting ready"
with open('wikipedia_wordfreq.txt','r') as f:
	for line in f:
		i = line.split("\t")
		term = i[0]
		freq = i[1]
		if(i[0].strip() == 'cats'):
			print 'yay'
        wordlist[term] = freq
 
print "Initialized"
print wordlist
doc = "This is a document about cats and dogs and all nice things in the world"
query = "cats and dogs"

print get_score(doc,query)