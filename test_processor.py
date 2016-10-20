# -*- coding: utf-8 -*-

'''
Test processor to see if the external canvas_processor code works.
'''

import canvas_processor
import spacy.en



def main():
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
    # Nubian message: https://d.lib.ncsu.edu/collections/catalog/nubian-message-2003-04-01/manifest  ***
    parser = spacy.en.English()
    item = canvas_processor.Manifest(
        uri='https://digital.library.villanova.edu/Item/vudl:14704/Manifest')
    # canvas = item.canvases[10]
    total = len(item.canvases)
    count = 1
    for canvas in item.canvases:
        print 'Processing canvas %s of %s' % (count, total)
        # print canvas['seeAlso']
        processed = canvas_processor.CanvasProcess(entity_parser=parser,
            canvas_obj=canvas, manifest_id=item.requested.uri)
        count += 1

if __name__ == '__main__':
    main()
