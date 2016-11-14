# -*- coding: utf-8 -*-
import os
import fnmatch
from PIL import Image
from tesserocr import PyTessBaseAPI
import concurrent.futures
import glob


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


def process_roll(folder_name):
    '''
    Process a folder of images for a roll.
    '''
    folder_base = str(folder_name.split('/')[-2])
    images = get_images(folder_name, 'tif')
    with concurrent.futures.ProcessPoolExecutor(3) as pool:
        for image in images:
            if os.path.exists(image):
                hocr_file = image.replace('tif', 'hocr')
                if os.path.exists(hocr_file):
                    pass
                else:
                    pool.submit(ocr_image, image, hocr_file, write=True)


def main():
    folders = glob.glob('/Volumes/IDA-IMAGES/source/PLB*/')
    for folder in folders:
        print 'Folder: %s' % folder
        process_roll(
            folder)
        # process_roll(
        #     '/Volumes/IDA-IMAGES/source/M-1011_R-09/')


if __name__ == '__main__':
    main()
