# -*- coding: utf-8 -*-

'''
Test processor to see if the external canvas_processor code works.
'''

import canvas_processor
import spacy.en
import spacy.matcher
from spacy.attrs import ORTH, LOWER
import ujson
from bs4 import BeautifulSoup


def main():
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
    # item = Manifest(
    #     uri='http://wellcomelibrary.org/iiif/b20086362/manifest')
    # print item.requested.uri
    # https://tomcrane.github.io/scratch/manifests/ida/m1011-santa-fe-1910-30.json
    # item = Manifest(uri='http://tomcrane.github.io/scratch/manifests/ida/m1011-san-juan-1920-22.json')
    # Americana: https://digital.library.villanova.edu/Collection/vudl:14572/IIIF
    # https://digital.library.villanova.edu/Item/vudl:354895/Manifest    ****
    # https://digital.library.villanova.edu/Item/vudl:14704/Manifest
    # Bod ephemera?
    # http://iiif.bodleian.ox.ac.uk/iiif/manifest/54b574dd-8be3-4388-a840-b824954cf161.json
    # http://wellcomelibrary.org/iiif/b24881843/manifest  ** Tewa Indians
    # Nubian message:
    # https://d.lib.ncsu.edu/collections/catalog/nubian-message-2003-04-01/manifest
    # ***
    data = ujson.loads(open('new_mexico.json').read())
    nlp = spacy.en.English()
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
        nlp.matcher.add(
            name,  # Entity ID: Not really used at the moment.
            z,   # Entity type: should be one of the types in the NER data
            # Arbitrary attributes. Currently unused.
            {"geonameid": geonameid},
            word_list
        )

    item = canvas_processor.Manifest(
        uri='http://mirador-dev.digtest.co.uk/test_c.json')
    # canvas = item.canvases[10]
    total = len(item.canvases)
    count = 1
    for canvas in item.canvases:
        print 'Processing canvas %s of %s' % (count, total)
        # print canvas['seeAlso']
        processed = canvas_processor.CanvasProcess(entity_parser=nlp,
                                                   canvas_obj=canvas, manifest_id=item.requested.uri, push=True)
        count += 1

if __name__ == '__main__':
    main()
