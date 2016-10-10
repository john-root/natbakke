import ujson

foo = './lib/python2.7/site-packages/spacy/data/en-1.1.0/vocab/gazetteer.json'

bar = ujson.loads(open(foo).read())

# format:
# list:
#		0 = token type
#		1 = unused dict
#		2 = list of lists
#			one for each token
#			i.e. [[{'lower':'lowercase'}], ['orth':'orth']]
# See: https://github.com/explosion/spaCy/blob/master/examples/matcher_example.py
# for an example dynamically loading an entry, for details of the basic format.

for key in bar:
	print key
	print bar[key]