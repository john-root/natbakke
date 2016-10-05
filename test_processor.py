# -*- coding: utf-8 -*-

'''
Test processor to see if the external canvas_processor code works.
'''

import canvas_processor


def main():
    # item = Manifest(
    #     uri='http://wellcomelibrary.org/iiif/b20086362/manifest')
    # print item.requested.uri
    # https://tomcrane.github.io/scratch/manifests/ida/m1011-santa-fe-1910-30.json
    # item = Manifest(uri='http://tomcrane.github.io/scratch/manifests/ida/m1011-san-juan-1920-22.json')
    item = canvas_processor.Manifest(
        uri='https://tomcrane.github.io/scratch/manifests/ida/m1011-santa-fe-1910-30.json')
    # canvas = item.canvases[10]
    total = len(item.canvases)
    count = 1
    for canvas in item.canvases:
        print 'Processing canvas %s of %s' % (count, total)
        processed = canvas_processor.CanvasProcess(
            canvas_obj=canvas, manifest_id=item.requested.uri)
        count += 1

if __name__ == '__main__':
    main()
