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


def initialise_spacy(matcher_json=None, geonames=False):
    '''
    Initialise a spacy parser, then add custom
    vocab to the matcher.
    '''
    parser = spacy.en.English()
    matcher = spacy.matcher.Matcher(parser.vocab)
    if geonames:
        featurecode_dict = build_featurecode_dict('GeoNames.htm')
    if matcher_json is not None:
        data = ujson.loads(open(matcher_json).read())
        # nlp = spacy.en.English()
        for item in data:
            name = item['name']
            geonameid = item['geonameid']
            name_tokens = item['asciiname'].split()
            word_list = []
            for token in name_tokens:
                word_dict = {LOWER: token.lower(), ORTH: token}
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
            add_list = [name, z, {"geonameid": geonameid}, [word_list]]
            print ujson.dumps(add_list, indent=4)
            matcher.add_pattern(
                ''.join(name.split()).lower(),
                word_list,
                label=name)
            matcher.add_entity(
                # Entity ID -- Helps you act on the match.
                ''.join(name.split()).lower(),
                # Arbitrary attributes (optional)
                {"ent_type": z,
                    "geonameid": geonameid},
                if_exists='update'
            )
    matcher.add_pattern(
        "narragansett",
        [{LOWER: "narragansett", ORTH: "Narragansett"}],
        label="Narragansett")
    matcher.add_entity(
        "narragansett",  # Entity ID -- Helps you act on the match.
        # Arbitrary attributes (optional)
        {"ent_type": "TRIBE",
            "wiki_en": "https://en.wikipedia.org/wiki/Narragansett_people"},
        if_exists='update'
    )
    matcher.add_pattern(
        "courdalene",
        [{LOWER: "cour", ORTH: "Cour"},
            {LOWER: "d'alene", ORTH: "D'Alene"}],
        label="Coeur d'Alene")
    matcher.add_pattern(
        "courdalene",
        [{LOWER: "coeur", ORTH: "Coeur"},
            {LOWER: "d'alene", ORTH: "d'Alene"}],
        label="Coeur d'Alene")
    matcher.add_entity(
        "courdalene",  # Entity ID -- Helps you act on the match.
        # Arbitrary attributes (optional)
        {"ent_type": "TRIBE",
            "wiki_en": "https://en.wikipedia.org/wiki/Coeur_d%27Alene_people"},
        if_exists='update'
    )
    return matcher, parser
