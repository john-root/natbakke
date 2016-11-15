# -*- coding: utf-8 -*-
import os
import fnmatch
from bs4 import BeautifulSoup
import re
import ftfy
from spacy_basics import initialise_spacy
import csv
import glob
import json
from collections import Counter
from PIL import Image
from tesserocr import PyTessBaseAPI
from enchant.checker import SpellChecker
from tribes_import import initialise_tribes


def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename

'''

Per folder:

read each image
check if there is ocr data
if not ocr the image
process hocr
generate full text and hocr
generate entities
gather stats

'''


def get_images(folder_name, ext):
    '''
    Return a list of images in folder with extenstion ext.
    '''
    image_list = []
    for filename in find_files(folder_name, '*.' + ext):
        if not os.path.basename(os.path.normpath(filename)).startswith('._'):
            image_list.append(os.path.normpath(filename))
    if image_list:
        return image_list


def ocr_image(imagefile, hocr_file, write=True):
    with PyTessBaseAPI() as api:
        image = Image.open(imagefile)
        api.SetImage(image)
        hocr_contents = api.GetHOCRText(0)
        if write:
            with open(hocr_file, 'w') as hocka:
                hocka.write(
                    hocr_contents.encode(
                        'ascii', 'xmlcharrefreplace')
                )
        return hocr_contents


def ocr_parse(hocr_data, text_file=None):
    text_list = []
    soup = BeautifulSoup(hocr_data, "html.parser")
    lines = soup.find_all("span", class_="ocr_line")
    count = 0
    conf_total = 0
    for line in lines:
        line_soup = BeautifulSoup(
            str(line), "html.parser")
        words = line_soup.find_all(
            "span", class_="ocrx_word")
        for word in words:
            count += 1
            word_soup = BeautifulSoup(
                str(word), "html.parser")
            text_list.append(
                ftfy.fix_text(word_soup.text))
            confidence = int(
                word_soup.span['title'].split(';')[1].split()[-1])
            conf_total = conf_total + confidence
    ocr_text = ' '.join(text_list)
    ocr_text_sub = re.sub(r'\s+', ' ', ocr_text)
    if text_file:
        with open(text_file, 'w') as texta:
            texta.write(
                ocr_text_sub.encode('ascii', 'replace'))
    if conf_total > 0 and count > 0:
        average_confidence = (conf_total / count)
    else:
        average_confidence = 0
    if average_confidence < 60:
        typewritten = False
    elif (average_confidence > 70 and len(ocr_text_sub) < 10):
        typewritten = False
    else:
        typewritten = True
    return average_confidence, typewritten, ocr_text_sub


def spelling(text):
    chkr = SpellChecker("en_US")
    chkr.set_text(text)
    words = text.split()
    num_words = len(words)
    err_list = []
    for err in chkr:
        err_list.append(err.word)
    num_errors = len(err_list)
    if num_words != 0:
        percent_wrong = float(num_errors) / float(num_words)
        # print 'Num errors: %s' % num_errors
        # print 'Num words: %s' % num_words
        # print 'Percentage wrong %s' % percent_wrong
        spell_percent = int(100 * (1 - percent_wrong))
        return spell_percent
    else:
        return None


def nlp_image(text, imagefile, parser, matcher, id):
    '''
    Do entity extraction and entity stats gathering for
    the text for an image.
    '''
    small_list = []
    rows = []
    parsed = parser(unicode(text))
    matches = matcher(parsed)
    for ent_id, label, start, end in matches:
        '''
        Grab the dict from the entity
        '''
        entity = matcher.get_entity(ent_id)
        orth = parser.vocab.strings[label]
        ent_type = entity["ent_type"]
        small_list.append(entity["ent_type"])
        cont_row = {'Entity_Orth': orth.encode('utf-8'),
                    'Entity_Label': ent_type,
                    'Source': id}
        rows.append(cont_row)
    for ent in parsed.ents:
        if ent.label_ not in ['TIME', 'PERCENT', 'CARDINAL', 'ORDINAL', 'QUANTITY', 'MONEY'] and len(ent.orth_) > 3:
            small_list.append(ent.label_)
            cont_row = {'Entity_Orth': ent.orth_.encode('utf-8'),
                        'Entity_Label': ent.label_,
                        'Source': id}
            rows.append(cont_row)
    number_ents = len(parsed.ents)
    c = Counter(small_list)
    stats = {}
    for item in c.items():
        z = list(item)
        stats[str(z[0])] = str(z[1])
    return number_ents, stats, rows


def process_image(imagefile, parser, matcher, folder_name):
    # text_file = imagefile.replace('jpg', 'txt')
    base = os.path.basename(imagefile).replace('.jpg', '')
    print 'Base: %s' % base
    if '_' in base:
        parts = base.split('_')
        id = ''.join(
            ['https://dlcs-ida.org/iiif-img/2/1/',
             folder_name + '_' + parts[1]])
    else:
        id = ''.join(
            ['https://dlcs-ida.org/iiif-img/2/1/',
             folder_name + '_' + base])
    hocr_file = imagefile #.replace('jpg', 'hocr')
    if os.path.exists(imagefile):
        if os.path.exists(hocr_file):
            hocr = open(hocr_file, 'r')
            hocr_data = hocr.read()
            hocr.close()
        else:
            hocr_data = ocr_image(imagefile, hocr_file, write=False)
    confidence, typewritten, text = ocr_parse(hocr_data)
    number_ents, stats, rows = nlp_image(text, imagefile, parser, matcher, id)
    accuracy = spelling(text)
    page = {}
    page['Average_confidence'] = confidence
    if typewritten:
        page['Entity_stats'] = stats
        page['Total_entities_found'] = number_ents
        if accuracy:
            page['Spelling_accuracy'] = accuracy
    else:
        page['Entity_stats'] = {}
        page['Total_entities_found'] = 0
    page['Typescript'] = typewritten
    page['Full_text_length'] = len(text)
    page['id'] = id

    print json.dumps(page, indent=4)
    return page, rows


def process_roll(folder_name, parser, matcher, writer, json_write=False):
    '''
    Process a folder of images for a roll.
    '''
    folder_base = str(folder_name.split('/')[-2])
    json_file = os.path.join(
        folder_name, folder_base + '.json')
    summary = []
    images = get_images(folder_name, 'hocr')
    for image in images:
        page, rows = process_image(image, parser, matcher, folder_base)
        if rows:
            for row in rows:
                writer.writerow(row)
        if page:
            summary.append(page)
    if json_write:
        with open(json_file, 'w') as outfile:
            print 'Writing %s' % json_file
            json.dump(
                summary, outfile, indent=4,
                sort_keys=True, separators=(',', ':'))


def main():
    csv_file = '/Users/matt.mcgrattan/Documents/tribe_names.csv'
    matcher, parser = initialise_tribes(csv_file)
    # parser = initialise_spacy()
    with open('output_tribes.csv', 'wb') as f:
        fieldnames = ['Entity_Orth', 'Entity_Label', 'Source']
        writer = csv.DictWriter(f, fieldnames=fieldnames, dialect='excel')
        writer.writeheader()
        # folders = glob.glob('/Volumes/IDA-IMAGES/source/[M, T]-*/')
        folders = glob.glob(
            '/users/matt.mcgrattan/Dropbox/Digirati/text/[M,T]-*/')
        for folder in folders:
            print 'Folder: %s' % folder
            # folders = ['/Volumes/IDA-IMAGES/source/M-1011_R-09/']
            process_roll(
                folder, parser, matcher, writer, json_write=True)


if __name__ == '__main__':
    main()
