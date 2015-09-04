import urllib
import HTMLParser

urlText = []
#Define HTML Parser
class parseText(HTMLParser.HTMLParser):
        
    def handle_data(self, data):
        if data != '\n':
            urlText.append(data)

#Create instance of HTML parser
lParser = parseText()
thisurl = "http://cis.poly.edu/cs6913"
lParser.feed(urllib.urlopen(thisurl).read())
lParser.close()
for item in urlText:
    print item
