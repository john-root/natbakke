# -*- coding: utf-8 -*-

import ujson
import json
import basics
import validators
import requests
from ocr_basics import get_words_alto, get_words_hocr, ocr_image
from parser_basics import ocr_to_annos
import hashlib
import os

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

    def __init__(self, canvas_obj, manifest_id, push=False):
        self.data_dir = './data/'
        self.push = push
        self.manifest_id = manifest_id
        self.canvas = Canvas(canvas_obj)
        self.id = self.canvas.canvas_obj['@id']
        self.canvas.get_width_height()
        # index the OCR data.
        self.index_ocr_data()
        if hasattr(self, 'word_index'):
            self.annotations = ocr_to_annos(
                self.ocr_text_sub, self.word_index, self.word_list, self.id, self.manifest_id)
            # save the annotations to a JSON file, using hash of canvas_id as filename
            if self.annotations:
                filename = os.path.join(self.data_dir, hashlib.md5(self.id).hexdigest() + '.json')
                with open(filename, 'w') as file:
                    file.write(json.dumps(self.annotations, indent=4))
                if self.push==True:
                    push_annos(self.annotations, self.id)
                else:
                    print json.dumps(self.annotations, indent=4)

    def index_ocr_data(self):
        '''
        Function: Generate an index of OCR words with their
        bounding boxes, and character offsets, plus OCR full text.

        Try to get Alto or hOCR data.

        If either exist, use those to generate the entity based
        annotation list.

        If no OCR available, generate the OCR by calling a function
        that uses tesseract to generate hOCR.

        Parse that.
        '''
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
        if hasattr(self.canvas, 'info_json'):
            self.canvas.hocr = ocr_image(self.canvas.info_json, self.id, self.data_dir)


def create_container(container_name, label, uri='https://annotation-dev.digtest.co.uk:443/w3c/'):
    '''
    Create a IIIF Container with a container name and label.

    Will default to Anno Dev server.
    '''
    container_headers = {'Slug': container_name,
                         'Content-Type': 'application/ld+json',
                         'Accept': 'application/ld+json;profile="http://www.w3.org/ns/anno.jsonld"'}
    container_dict = {'@context': 'http://www.w3.org/ns/anno.jsonld',
                      'type': 'AnnotationCollection',
                      'label': label}
    container_body = json.dumps(container_dict)
    print 'JSON for container create: %s' % container_body
    print 'Container headers: %s' % container_headers
    x = requests.get(uri + container_name + '/')
    if x.status_code == 200:
        print 'Container exists'
        return x.status_code, x.content
    else:
        r = requests.post(
            uri, headers=container_headers, data=container_body)
        print 'Container create status: %s' % r.status_code
        return r.status_code, r.content


def create_anno(container_name, anno_body, uri='https://annotation-dev.digtest.co.uk:443/w3c/'):
    anno_headers = {'Content-Type': 'application/ld+json',
                    'Accept': 'application/ld+json;profile="http://www.w3.org/ns/anno.jsonld"'}
    print 'JSON for anno create: %s' % anno_body
    print 'Anno headers: %s' % anno_headers
    r = requests.post(
        uri + '/' + container_name + '/', headers=anno_headers, data=anno_body)
    print 'Anno create status: %s' % r.status_code
    return r.status_code, r.content


def push_annos(annotation_list, canvas_id):
    for annotation in annotation_list:
        body = json.dumps(annotation, indent=4)
        target = canvas_id
        targ_hash = hashlib.md5(target).hexdigest() + '_1'
        try:
            status, data = create_container(targ_hash, target)
            if status == 200 or status == 201:
                anno_status, anno_data = create_anno(
                    targ_hash, body)
                print 'Anno create status: %s' % anno_status
                print 'Anno create return %s' % anno_data
        except:
            print "Something went wrong."