from pygoogle import pygoogle
query = raw_input("Enter the Query: ")
g = pygoogle(query)
g.pages = 1
print g.get_urls()