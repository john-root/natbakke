import spacy.en
from bs4 import BeautifulSoup
import spacy.matcher
from spacy.attrs import ORTH, LOWER
import ujson


def build_featurecode_dict(file_name):
    '''
    Build geonames featurecode dict
    that can be used to match featurecodes
    with Spacy entity classes.
    '''
    featurecodes = open(file_name).read()
    soup = BeautifulSoup(featurecodes, 'html.parser')
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
    return featurecode_dict


def initialise_spacy(matcher_json):
    '''
    Initialise a spacy parser, then add custom
    vocab to the matcher.
    '''
    parser = spacy.en.English()
    featurecode_dict = build_featurecode_dict('GeoNames.htm')
    # data = ujson.loads(open('new_mexico.json').read())
    data = ujson.loads(open(matcher_json).read())
    # nlp = spacy.en.English()
    for item in data:
        name = item['name']
        geonameid = item['geonameid']
        name_tokens = item['asciiname'].split()
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
        parser.matcher.add(
            name,  # Entity ID: Not really used at the moment.
            z,   # Entity type: should be one of the types in the NER data
            # Arbitrary attributes. Currently unused.
            {"geonameid": geonameid},
            word_list
        )
    return parser