import os
import fnmatch
import subprocess
from bs4 import BeautifulSoup
import re
import ftfy
from spacy_basics import initialise_spacy
import csv
import glob
import json
from collections import Counter


def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename


def main():
    parser = initialise_spacy()
    with open('output.csv', 'wb') as f:
        fieldnames = ['Entity_Orth', 'Entity_Label', 'Source']
        writer = csv.DictWriter(f, fieldnames=fieldnames, dialect='excel')
        writer.writeheader()
        summary = []
        for filename in find_files('/Users/matt.mcgrattan/Documents/IDA-NARA_files/M-1473_R-09/', '*.jpg'):
            if not os.path.basename(os.path.normpath(filename)).startswith('._'):
                print 'Input Image: ', os.path.basename(os.path.normpath(filename))
                text_file = os.path.join('/Users/matt.mcgrattan/Documents/IDA-NARA_files/', str(
                    filename.split("/")[-2]), os.path.basename(os.path.normpath(filename)).replace('.jpg', ''))
                hocr_file = os.path.join(
                    '/tmp/', os.path.basename(os.path.normpath(filename)).replace('.jpg', ''))
                try:
                    command = ['tesseract', filename, hocr_file, 'hocr']
                    subprocess.check_output(command, stderr=subprocess.STDOUT)
                    source_hocr = hocr_file + '.hocr'
                    text_file = text_file + '.txt'
                    small_list = []
                    page = {}
                    with open(source_hocr, 'r') as foo:
                        hocr_contents = foo.read()
                        text_list = []
                        soup = BeautifulSoup(hocr_contents, "html.parser")
                        lines = soup.find_all("span", class_="ocr_line")
                        count = 0
                        conf_total = 0
                        for line in lines:
                            line_soup = BeautifulSoup(str(line), "html.parser")
                            words = line_soup.find_all(
                                "span", class_="ocrx_word")
                            for word in words:
                                count += 1
                                word_soup = BeautifulSoup(
                                    str(word), "html.parser")
                                text_list.append(ftfy.fix_text(word_soup.text))
                                confidence = int(
                                    word_soup.span['title'].split(';')[1].split()[-1])
                                conf_total = conf_total + confidence
                        ocr_text = ' '.join(text_list)
                        ocr_text_sub = re.sub(r'\s+', ' ', ocr_text)
                        # print ocr_text_sub
                        thing = parser(ocr_text_sub)
                        for ent in thing.ents:
                            small_list.append(ent.label_)
                            if ent.label_ not in ['TIME', 'PERCENT', 'CARDINAL', 'ORDINAL', 'QUANTITY', 'MONEY'] and len(ent.orth_) > 3:
                                cont_row = {'Entity_Orth': ent.orth_.encode('utf-8'),
                                            'Entity_Label': ent.label_,
                                            'Source': filename}
                                writer.writerow(cont_row)
                        average_confidence = (conf_total / count)
                        number_ents = len(thing.ents)
                        c = Counter(small_list)
                        stats = {}
                        for item in c.items():
                            z = list(item)
                            stats[str(z[0])] = str(z[1])
                        page['File'] = filename
                        page['Average confidence'] = average_confidence
                        page['Total entities found'] = number_ents
                        page['Entity stats'] = stats
                        page['Full text'] = ocr_text_sub
                        print json.dumps(page, indent=4)
                        summary.append(page)
                except:
                    pass
            else:
                print 'DODGY:', filename
        with open('summary.json', 'w') as outfile:
            json.dump(summary, outfile, indent=4, sort_keys=True, separators=(',', ':'))


if __name__ == '__main__':
    main()
