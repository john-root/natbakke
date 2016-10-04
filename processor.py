# -*- coding: utf-8 -*-

import ujson
# import hocr_functions_refactor
# import manifest_ner
# import codecs
import basics
import validators
import requests
from ocr_basics import get_words_alto, get_words_hocr, ocr_image
from parser_basics import ocr_to_annos


class Manifest():

    def __init__(self, uri):
        self.requested = basics.IIIF_Manifest(uri)
        self.manifest_obj = ujson.loads(self.requested.source_data)
        self.canvases = basics.get_canvases(self.manifest_obj)


class Canvas():

    def __init__(self, canvas_obj):
        self.canvas_obj = canvas_obj

    def get_info_json(self):
        self.info_json_uri = self.canvas_obj[
            'images'][0]['resource']['service']['@id']
        if validators.url(self.info_json_uri) is True:
            try:
                self.info_json = requests.get(self.info_json_uri).json()
            except:
                print "Could not get info.json"

    def get_width_height(self):
        try:
            self.height = self.info_json['height']
            self.width = self.info_json['width']
        except AttributeError:
            self.get_info_json()
            self.get_width_height()

    def get_seeAlsos(self):
        try:
            if isinstance(self.canvas_obj['seeAlso'], list):
                for seeAlso in self.canvas_obj['seeAlso']:
                    self.identify_service(seeAlso)
            else:
                self.identify_service(self.canvas_obj['seeAlso'])
        except KeyError:
            print 'This canvas has no seeAlso.'

    def identify_service(self, service):
        if 'alto' in service['profile'].lower():
            self.alto_uri = service['@id']
        elif 'hocr' in service['profile'].lower():
            self.hocr_uri = service['@id']
        else:
            print 'Unknown'

    def get_alto(self):
        self.get_seeAlsos()
        if hasattr(self, 'alto_uri'):
            if validators.url(self.alto_uri)is True:
                r = requests.get(self.alto_uri)
                r.raise_for_status()
                self.alto = r.content

    def get_hocr(self):
        self.get_seeAlsos()
        if hasattr(self, 'hocr_uri'):
            if validators.url(self.hocr_uri)is True:
                r = requests.get(self.hocr_uri)
                r.raise_for_status()
                self.hocr = r.content


class CanvasProcess():

    '''
    Could probably run these in parallel to stop the OCR pipeline
    from being a bottleneck, e.g. run 4 canvases at once.
    '''

    def __init__(self, canvas_obj, manifest_id):
        self.manifest_id = manifest_id
        self.canvas = Canvas(canvas_obj)
        self.id = self.canvas.canvas_obj['@id']
        self.canvas.get_width_height()
        self.index_ocr_data()
        if hasattr(self, 'word_index'):
            self.annotations = ocr_to_annos(self.ocr_text_sub, self.word_index, self.word_list, self.id, self.manifest_id)

    def index_ocr_data(self):
        self.canvas.get_alto()
        self.canvas.get_hocr()
        if hasattr(self.canvas, 'alto'):
            self.word_index, self.word_list, self.ocr_text, self.ocr_text_sub = get_words_alto(
                self.canvas)
        elif hasattr(self.canvas, 'hocr'):
            self.word_index, self.word_list, self.ocr_text, self.ocr_text_sub = get_words_hocr(
                self.canvas)
        else:
            self.generate_ocr()
            self.word_index, self.word_list, self.ocr_text, self.ocr_text_sub = get_words_hocr(
                self.canvas)


    def generate_ocr(self):
        print 'OCR-ing'
        if hasattr(self.canvas, 'info_json'):
            self.canvas.hocr = ocr_image(self.canvas.info_json)


def push_annos(annotation_list):
    for annotation in annotation_list:
        body = json.dumps(annotation, indent=4)
        print body
        # try:
        #     status, data = create_container(targ_hash, target)
        #     if status == 200 or status == 201:
        #         anno_status, anno_data = create_anno(
        #             targ_hash, body)
        #         print 'Anno create status: %s' % anno_status
        #         print 'Anno create return %s' % anno_data
        # except:
        #     print "Something went wrong."

def main():
    # item = Manifest(
    #     uri='http://wellcomelibrary.org/iiif/b20086362/manifest')
    # print item.requested.uri
    item = Manifest(
        uri='http://tomcrane.github.io/scratch/manifests/ida/m1011-san-juan-1920-22.json')
    # canvas = item.canvases[10]
    for canvas in item.canvases:
        processed = CanvasProcess(canvas_obj=canvas, manifest_id=item.requested.uri)
        push_annos(processed.annotations)

if __name__ == '__main__':
    main()
