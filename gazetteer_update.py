# -*- coding: utf-8 -*-
import ujson

from bs4 import BeautifulSoup
foo = open('GeoNames.htm').read()
soup = BeautifulSoup(foo, 'html.parser')
tables = soup.find_all('table')
table = tables[1]
rows = table.find_all('tr')
featurecode_dict = {}

for row in rows:
    if row.find_all('th'):
        header = row.find_all('a')
        item_type = header[0].get('name')
    else:
        header = row.find_all('a')
        try:
            item_type = header[0].get('name')
            if item_type.split('.')[0] in ['A', 'P']:
                featurecode_dict[item_type.split('.')[1]] = 'GPE'
            elif item_type.split('.')[0] in ['L', 'R', 'S']:
                featurecode_dict[item_type.split('.')[1]] = 'FAC'
            else:
                featurecode_dict[item_type.split('.')[1]] = 'LOC'
        except:
            pass


# foo = './lib/python2.7/site-packages/spacy/data/en-1.1.0/vocab/gazetteer.json'


# format:
# list:
#       0 = token type
#       1 = unused dict
#       2 = list of lists
#           one for each token
#           i.e. [[{'lower':'lowercase'}], ['orth':'orth']]
# See: https://github.com/explosion/spaCy/blob/master/examples/matcher_example.py
# for an example dynamically loading an entry, for details of the basic format.

# gazetteer = ujson.loads(open(foo).read())

usa = ujson.loads(open('gb.json').read())

token_dict = {}
for item in usa:
    name_tokens = item['asciiname'].split()
    token_list = []
    word_list = []
    for token in name_tokens:
        word_dict = [{"lower": token.lower()}, {"orth": token}]
        word_list.append(word_dict)
    try:
        z = featurecode_dict[item['feature code']]
    except:
        try:
            if item['feature class'] in ['A', 'P']:
                z = 'GPE'
            elif item['feature class'] in ['L', 'R', 'S']:
                z = 'FAC'
            else:
                z = 'LOC'
        except:
            pass
    if z:
        token_list.append(z)
    token_list.append({})
    token_list.append(word_list)
    token_dict[item['name']] = token_list

with open('gb_gazetteer.json', 'w') as export:
    ujson.dump(token_dict, export, sort_keys=True, indent=4)
