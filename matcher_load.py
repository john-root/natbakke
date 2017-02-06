# from __future__ import unicode_literals, print_function

import spacy.en
import spacy.matcher
from spacy.attrs import ORTH, TAG, LOWER, IS_ALPHA, FLAG63
import ujson

data = ujson.loads(open('new_mexico.json').read())
nlp = spacy.en.English()

for item in data:
    name = item['name']
    geonameid = item['geonameid']
    name_tokens = item['asciiname'].split()
    token_list = []
    word_list = []
    for token in name_tokens:
        word_dict = [{LOWER: token.lower()}, {ORTH: token}]
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
    nlp.matcher.add(
        name,  # Entity ID: Not really used at the moment.
        z,   # Entity type: should be one of the types in the NER data
        {"geonameid": geonameid},  # Arbitrary attributes. Currently unused.
        word_list
    )
