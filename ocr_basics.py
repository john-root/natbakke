from bs4 import BeautifulSoup
import re
import ftfy
from io import open as iopen
import hashlib
import requests
import subprocess
import os


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
    char_count = 1  # keep a running count of character offset
    for line in lines:
        # parse each line with BS4
        line_soup = BeautifulSoup(str(line), "html.parser")
        word_soup = line_soup.find_all('string')
        for word in word_soup:
            count += 1
            word_dict = {}  # build a dict for each word
            word_dict['text'] = word['content']
            word_dict['id'] = str(count)  # running ID
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
    word_index = [{item['id']: range(
        int(item['start_idx']), int(item['end_idx']))} for item in word_list]
    return word_index, word_list, ocr_text, ocr_text_sub


def get_words_hocr(canvas):
    '''
    Returns a big list of words with
    text, coordinates, xywh bounding box,
    confidence, identifier, line number.

    Input: hOCR (html)

    Output: list of dictionaries of words
            full text.
    '''
    soup = BeautifulSoup(canvas.hocr, "html.parser")
    lines = soup.find_all("span", class_="ocr_line")
    word_list = []
    text_words = []
    # iterate through lines in the hOCR
    char_count = 0  # keep a running count of character offset
    for line in lines:
        # parse each line with BS4
        line_soup = BeautifulSoup(str(line), "lxml")
        # store line number for later
        number = line_soup.span['id'].split('_')[-1]
        # Parse with BS4 and extract all words from line.
        words = line_soup.find_all("span", class_="ocrx_word")
        for word in words:
            word_dict = {}
            # parse each word with BS4
            word_soup = BeautifulSoup(str(word), "lxml")
            # build a dictionary of word properties
            word_dict['line_number'] = number
            word_dict['bbox'] = word_soup.span[
                'title'].split(';')[0].split()[1:]
            word_dict['start_x'] = int(word_dict['bbox'][0])
            word_dict['start_y'] = int(word_dict['bbox'][1])
            word_dict['end_x'] = int(word_dict['bbox'][2])
            word_dict['end_y'] = int(word_dict['bbox'][3])
            word_dict['width'] = word_dict['end_x'] - word_dict['start_x']
            word_dict['height'] = word_dict['end_y'] - word_dict['start_y']
            word_dict['xywh'] = ','.join(
                [str(word_dict['start_x']),
                 str(word_dict['start_y']),
                 str(word_dict['width']),
                 str(word_dict['height'])])
            word_dict['text'] = ftfy.fix_text(word_soup.text)
            word_dict['start_idx'] = str(char_count)
            word_dict['end_idx'] = str(char_count + len(word_dict['text']))
            char_count = char_count + len(word_dict['text']) + 1
            word_dict['id'] = word_soup.span['id'].split('_')[-1]
            word_dict['confidence'] = word_soup.span[
                'title'].split(';')[1].split()[-1]
            word_list.append(word_dict)
            # build a simple whitespaced text
            # for use in entity extraction, etc.
            text_words.append(word_dict['text'])
    ocr_text = ' '.join(text_words)
    ocr_text_sub = re.sub(r'\s+', ' ', ocr_text)
    word_index = [
        {x['id']: range(int(x['start_idx']), int(x['end_idx']))} for x in word_list]
    return word_index, word_list, ocr_text, ocr_text_sub


def ocr_image(info_json):
    image_id = info_json['@id']
    fullfull = ''.join([image_id, '/full/full/0/default.jpg'])
    file_name = hashlib.md5(image_id).hexdigest() + '.jpg'
    get_image(fullfull, file_name)
    result = tesseract_image(file_name)
    if result:
        os.remove(file_name)
        return result
    else:
        return None


def tesseract_image(file_name):
    '''
    '''
    command = ['/usr/local/bin/tesseract', file_name, 'stdout', 'hocr']
    print command
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    result = proc.communicate()[0]
    return result


def get_image(fullfull, file_name):
    r = requests.get(fullfull)
    r.raise_for_status
    if r.status_code == 200:
        with iopen(file_name, 'wb') as file:
            file.write(r.content)
