# -*- coding: utf-8 -*-

# import lxml
from bs4 import BeautifulSoup
import re
import ftfy # for fixing badly encoded text
import ujson
# import hocr_functions_refactor
# import manifest_ner
# import spacy.en
# import hashlib
# import codecs
import basics
import validators
import requests


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
        if isinstance(self.canvas_obj['seeAlso'], list):
            for seeAlso in self.canvas_obj['seeAlso']:
                self.identify_service(seeAlso)
        else:
            self.identify_service(self.canvas_obj['seeAlso'])

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


def get_words_alto(canvas, verbose=False):
    '''Rewrite using Beautiful Soup

    Returns a big list of words with
    text, coordinates, xywh bounding box,
    confidence, identifier, line number.

    Input: Alto (xml), width and height of original

    Output: list of dictionaries of words
            full text.
    '''
    soup = BeautifulSoup(canvas.alto, "html.parser")
    attributes_dictionary = soup.find('page').attrs
    # source image height and width
    srcW = attributes_dictionary['width']
    srcH = attributes_dictionary['height']
    original_width = canvas.width
    original_height = canvas.height
    # scale factor to transform Alto coordinates
    # to pixels.
    scaleW = float(original_width) / float(srcW)
    scaleH = float(original_height) / float(srcH)
    # get the lines from the Alto.
    lines = soup.find_all("textline")
    word_list = []
    text_words = []
    # iterate through lines in the hOCR
    count = 0  # keep a running number of the words
    char_count = 1 # keep a running count of character offset
    for line in lines:
        # parse each line with BS4
        line_soup = BeautifulSoup(str(line), "html.parser")
        word_soup = line_soup.find_all('string')
        for word in word_soup:
            count += 1
            word_dict = {}  # build a dict for each word
            word_dict['text'] = word['content']
            word_dict['id'] = str(count)  # running ID
            word_dict['idx'] = str(char_count)
            char_count = char_count + len(word['content']) + 1
            x = int(float(word['hpos']) * scaleW)
            y = int(float(word['vpos']) * scaleH)
            w = int(float(word['width']) * scaleW)
            h = int(float(word['height']) * scaleH)
            # xwyh for target or fragment
            word_dict['xywh'] = ','.join([str(x), str(y), str(w), str(h)])
            # add the dict to the big list
            word_list.append(word_dict)
            # join the text together to return a text block
            text_words.append(word['content'])
    ocr_text = ' '.join(text_words)
    ocr_text_sub = re.sub(r'\s+', ' ', ocr_text)
    return word_list, ocr_text, ocr_text_sub


class CanvasProcess():
    def __init__(self, canvas_obj):
        self.canvas = Canvas(canvas_obj)
        self.canvas.get_width_height()
        self.index_ocr_data()

    def index_ocr_data(self):
        self.canvas.get_alto()
        self.canvas.get_hocr()
        if hasattr(self.canvas, 'alto'):
            words, ocr, ocr_sub = get_words_alto(self.canvas)
            print words
        elif hasattr(self.canvas, 'hocr'):
            words, ocr, ocr_sub = get_words_hocr(self.canvas)
            print words
        else:
            print 'Will need to OCR from images.'



def main():
    item = Manifest(
        uri='http://wellcomelibrary.org/iiif/b20086362/manifest')
    CanvasProcess(canvas_obj=item.canvases[24])


if __name__ == '__main__':
    main()
