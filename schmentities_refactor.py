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


def csv_init(f):
    '''
    Initialise the CSV file by creating header row
    if one doesn't already exist.
    '''
    reader = csv.reader(f)
    headers = reader.next()
    if headers[0] == 'Entity_Orth':
        print 'Got headers'
    else:
        fieldnames = ['Entity_Orth', 'Entity_Label', 'Source']
        writer = csv.DictWriter(f, fieldnames=fieldnames, dialect='excel')
        writer.writeheader()


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


def ocr_image(imagefile, write=True):
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


def nlp_image(text, imagefile, parser):
    '''
    Do entity extraction and entity stats gathering for
    the text for an image.
    '''
    small_list = []
    rows = []
    parsed = parser(unicode(text))
    for ent in parsed.ents:
        if ent.label_ not in ['TIME', 'PERCENT', 'CARDINAL', 'ORDINAL', 'QUANTITY', 'MONEY'] and len(ent.orth_) > 3:
            small_list.append(ent.label_)
            cont_row = {'Entity_Orth': ent.orth_.encode('utf-8'),
                        'Entity_Label': ent.label_,
                        'Source': imagefile}
            rows.append(cont_row)
    number_ents = len(parsed.ents)
    c = Counter(small_list)
    stats = {}
    for item in c.items():
        z = list(item)
        stats[str(z[0])] = str(z[1])
    print number_ents
    print stats
    print rows
    return number_ents, stats, rows


def process_image(imagefile, parser):
    # text_file = imagefile.replace('jpg', 'txt')
    hocr_file = imagefile.replace('jpg', 'hocr')
    if os.path.exists(imagefile):
        if os.path.exists(hocr_file):
            hocr = open(hocr_file, 'r')
            hocr_data = hocr.read()
            hocr.close()
        else:
            hocr_data = ocr_image(imagefile, write=False)
    confidence, typewritten, text = ocr_parse(hocr_data)
    nlp_image(text, imagefile, parser)


def process_roll(folder_name, csv_file, parser):
    '''
    Process a folder of images for a roll.
    '''
    folder_base = str(folder_name.split('/')[-2])
    json_file = os.path.join(
        folder_name, folder_base + '.json')
    print 'JSON summary: %s' % json_file
    summary = []
    with open(csv_file, 'rw+') as f:
        csv_init(f)
    images = get_images(folder_name, 'jpg')
    for image in images:
        process_image(image, parser)


def main():
    parser = initialise_spacy()
    process_roll(
        '/Users/matt.mcgrattan/Documents/IDA-NARA_files/M-1473_R-13/',
        'output.csv', parser)


def old_main():
    parser = initialise_spacy()
    foo = glob.glob(
        '/Users/matt.mcgrattan/Documents/IDA-NARA_files/M-1473_R-13/')
    csv_file = 'output.csv'
    with open(csv_file, 'wb') as f:
        fieldnames = ['Entity_Orth', 'Entity_Label', 'Source']
        writer = csv.DictWriter(f, fieldnames=fieldnames, dialect='excel')
        writer.writeheader()
        for bar in foo:
            # csv_file = str(bar.split('/')[-2]) + '.csv'
            json_file = os.path.join(bar, str(bar.split('/')[-2]) + '.json')
            summary = []
            for filename in find_files(bar, '*.jpg'):
                if not os.path.basename(os.path.normpath(filename)).startswith('._'):
                    print 'Input Image: ', os.path.basename(os.path.normpath(filename))
                    text_file = filename.replace('jpg', 'txt')
                    hocr_file = filename.replace('jpg', 'hocr')
                    with PyTessBaseAPI() as api:
                        image = Image.open(filename)
                        api.SetImage(image)
                        hocr_contents = api.GetHOCRText(0)
                        with open(hocr_file, 'w') as hocka:
                            hocka.write(
                                hocr_contents.encode(
                                    'ascii', 'xmlcharrefreplace')
                            )
                        small_list = []
                        page = {}
                        text_list = []
                        soup = BeautifulSoup(hocr_contents, "html.parser")
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
                        with open(text_file, 'w') as texta:
                            texta.write(
                                ocr_text_sub.encode('ascii', 'replace'))
                        thing = parser(unicode(ocr_text_sub))
                        for ent in thing.ents:
                            small_list.append(ent.label_)
                            if ent.label_ not in ['TIME', 'PERCENT', 'CARDINAL', 'ORDINAL', 'QUANTITY', 'MONEY'] and len(ent.orth_) > 3:
                                cont_row = {'Entity_Orth': ent.orth_.encode('utf-8'),
                                            'Entity_Label': ent.label_,
                                            'Source': filename}
                                writer.writerow(cont_row)
                        if conf_total > 0 and count > 0:
                            average_confidence = (conf_total / count)
                        else:
                            average_confidence = 0
                        number_ents = len(thing.ents)
                        c = Counter(small_list)
                        stats = {}
                        for item in c.items():
                            z = list(item)
                            stats[str(z[0])] = str(z[1])
                        if average_confidence < 60:
                            typewritten = False
                        elif (average_confidence > 70 and len(ocr_text_sub) < 10):
                            typewritten = False
                        else:
                            typewritten = True
                        # crimes against Python
                        base = os.path.basename(filename).replace('.jpg', '')
                        parts = base.split('_')
                        roll_bits = parts[0].split('R')
                        roll_bits[0] = roll_bits[0][
                            0:1] + '-' + roll_bits[0][1:]
                        id = ''.join(
                            ['https://dlcs-ida.org/iiif-img/2/1/', '_R-'.join(roll_bits) + '_' + parts[1]])
                        page['id'] = id
                        page['Average_confidence'] = average_confidence
                        page['Total_entities_found'] = number_ents
                        page['Entity_stats'] = stats
                        page['Typescript'] = typewritten
                        page['Full_text_length'] = len(ocr_text_sub)
                        print json.dumps(page, indent=4)
                        summary.append(page)
                else:
                    print 'DODGY:', filename
            with open(json_file, 'w') as outfile:
                json.dump(
                    summary, outfile, indent=4, sort_keys=True, separators=(',', ':'))


if __name__ == '__main__':
    main()
