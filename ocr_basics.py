from bs4 import BeautifulSoup
import re
import ftfy
import hashlib
import requests
import subprocess
import os
from PIL import Image
from io import BytesIO


def get_words_alto(canvas, verbose=False):
    '''Rewrite using Beautiful Soup

    Returns a big list of words with
    text, coordinates, xywh bounding box,
    confidence, identifier, line number.

    Input: Alto (xml), width and height of original

    Output: list of dictionaries of words
            full text.

    ToDo: combine the two word indexes into one.
    ToDo: combine both hocr and alto functions into one.

    ** Need to add confidence or broken **
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
    # iterate through lines in the Alto
    count = 0  # keep a running number of the words
    char_count = 0  # keep a running count of character offset
    line_count = 0  # keep a running count of lines.
    for line in lines:
        line_count += 1
        # parse each line with BS4
        line_soup = BeautifulSoup(str(line), "html.parser")
        word_soup = line_soup.find_all('string')
        for word in word_soup:
            count += 1
            word_dict = {}  # build a dict for each word
            word_dict['text'] = word['content']
            word_dict['id'] = str(count)  # running ID
            word_dict['line_number'] = line_count
            word_dict['start_idx'] = str(char_count)
            word_dict['end_idx'] = str(char_count + len(word_dict['text']))
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
            text_words.append(word_dict['text'])
    ocr_text = ' '.join(text_words)
    ocr_text_sub = re.sub(r'\s+', ' ', ocr_text)
    # index with the ID of each word, and the range it spans in terms
    # of character offset from start of text.
    # e.g. {11: [22,23,24]} = the 11th word, which spans characters 22 - 24.
    # used to match Spacy.io tokens (which have an index that gives the char
    # offset) to OCR words and thus bounding boxes.
    word_index = [{item['id']: range(
        int(item['start_idx']), int(item['end_idx']))} for item in word_list]
    return word_index, word_list, ocr_text, ocr_text_sub


def get_words_hocr(canvas, scale_factor=None):
    '''
    Returns a big list of words with
    text, coordinates, xywh bounding box,
    confidence, identifier, line number.

    Input: hOCR (html)

    Output: list of dictionaries of words
            full text.

    ToDo: combine the two word indexes into one.
    ToDo: combine both hocr and alto functions into one.
    '''
    soup = BeautifulSoup(canvas.hocr, "html.parser")
    lines = soup.find_all("span", class_="ocr_line")
    word_list = []
    text_words = []
    count = 0  # keep a running number of the words
    # iterate through lines in the hOCR
    char_count = 0  # keep a running count of character offset
    line_count = 0  # start at 1 below, do we care?
    for line in lines:
        line_count += 1
        # parse each line with BS4
        line_soup = BeautifulSoup(str(line), "lxml")
        # print 'hOCR Line: %s' % line
        # store line number for later
        # this is potentially fragile -- should possibly
        # just generate a number, check against
        # ocracoke hCOR, for example.
        # number = line_soup.span['id'].split('_')[-1]
        # Parse with BS4 and extract all words from line.
        words = line_soup.find_all("span", class_="ocrx_word")
        for word in words:
            count += 1
            word_dict = {}
            # parse each word with BS4
            word_soup = BeautifulSoup(str(word), "lxml")
            # build a dictionary of word properties
            word_dict['line_number'] = line_count  # number
            word_dict['bbox'] = word_soup.span[
                'title'].split(';')[0].split()[1:]
            word_dict['start_x'] = int(word_dict['bbox'][0])
            word_dict['start_y'] = int(word_dict['bbox'][1])
            word_dict['end_x'] = int(word_dict['bbox'][2])
            word_dict['end_y'] = int(word_dict['bbox'][3])
            word_dict['width'] = word_dict['end_x'] - word_dict['start_x']
            word_dict['height'] = word_dict['end_y'] - word_dict['start_y']
            if scale_factor:
                print 'Scale factor: %s' % scale_factor
            if scale_factor:
                start_x = str(int(word_dict['start_x'] * scale_factor))
                start_y = str(int(word_dict['start_y'] * scale_factor))
                width = str(int(word_dict['width'] * scale_factor))
                height = str(int(word_dict['height'] * scale_factor))
            else:
                start_x = str(word_dict['start_x'])
                start_y = str(word_dict['start_y'])
                width = str(word_dict['width'])
                height = str(word_dict['height'])
            word_dict['xywh'] = ','.join(
                [
                    start_x,
                    start_y,
                    width,
                    height
                ])
            word_dict['text'] = ftfy.fix_text(word_soup.text)
            word_dict['start_idx'] = str(char_count)
            word_dict['end_idx'] = str(char_count + len(word_dict['text']))
            char_count = char_count + len(word_dict['text']) + 1
            word_dict['id'] = count  # word_soup.span['id'].split('_')[-1]
            word_dict['confidence'] = word_soup.span[
                'title'].split(';')[1].split()[-1]
            # print 'Confidence: %s' % word_dict['confidence']
            word_list.append(word_dict)
            # build a simple whitespaced text list
            # for use in entity extraction, etc.
            text_words.append(word_dict['text'])
    ocr_text = ' '.join(text_words)
    ocr_text_sub = re.sub(r'\s+', ' ', ocr_text)
    # index with the ID of each word, and the range it spans in terms
    # of character offset from start of text.
    # e.g. {11: [22,23,24]} = the 11th word, which spans characters 22 - 24.
    # used to match Spacy.io tokens (which have an index that gives the char
    # offset) to OCR words and thus bounding boxes.
    word_index = [
        {x['id']: range(int(x['start_idx']), int(x['end_idx']))} for x in word_list]
    return word_index, word_list, ocr_text, ocr_text_sub


def ocr_image(info_json, canvas_id, image_dir, data_dir):
    '''
    Read the info.json

    Generate a full/full image path from the @id
    Get this file and save to disk.
    Run tesseract over it.
    Return the hOCR for processing.

    Use the hash of the canvas id for the hocr filename.
    '''
    image_id = info_json['@id']
    fullfull = ''.join([image_id, '/full/full/0/default.jpg'])
    file_name = os.path.join(
        image_dir, hashlib.md5(image_id).hexdigest() + '.jpg')
    hocr_file = os.path.join(data_dir, hashlib.md5(canvas_id).hexdigest())
    try:
        width, height = get_image(fullfull, file_name)
        if width:
            scale_factor = float(info_json['width']) / float(width)
            # print 'Width %s' % width
            # print 'Height %s' % height
            # print 'Info json width %s' % info_json['width']
            # print 'Info json height %s' % info_json['height']
            # print 'Generated scale factor %s' % scale_factor
    except:
        pass
    if os.path.exists(file_name):
        result = tesseract_image(file_name, hocr_file)
        if result:
            '''
            Is this premature?
            '''
            # print result
            print 'Removing file: %s' % file_name
            os.remove(file_name)
            if scale_factor:
                return scale_factor, result
            else:
                return None, result
        else:
            return None
    else:
        print 'File missing'
        return None


def tesseract_image(file_name, hocr_file):
    '''
    Run tesseract in a subprocess, reading the jpeg
    and writing to an hoCR file.

    When done, read the hOCR and return.
    '''
    command = ['tesseract', file_name, hocr_file, 'hocr']
    # print command
    proc = subprocess.check_output(command)
    with open(hocr_file+'.hocr') as hocr:
        ocr_data = hocr.read()
        return ocr_data


def get_image(fullfull, file_name):
    r = requests.get(fullfull, stream=False)
    r.raise_for_status
    if r.status_code == 200:
        i = Image.open(BytesIO(r.content))
        try:
            width, height = i.size
        except:
            pass
        print 'Format: %s' % i.format
        if i.format == 'JPEG':
            i.save(file_name)
        if width and height:
            return width, height
