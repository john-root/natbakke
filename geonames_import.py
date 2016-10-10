# -*- coding: utf-8 -*-
import csv
import sys
import ujson

'''
Grab the data from the US export from Geonames,
filter out just the New Mexico data, and dump
to an JSON file.
'''

# need this because of some huge fields,
# especially alternatenames, which can
# include Unicode, e.g. cyrillic and
# arabic transliterations.
csv.field_size_limit(sys.maxsize)

text_file = open('US.txt')

# field list, as no header row in tab delimited txt file.
fields = ['geonameid', 'name', 'asciiname', 'alternatenames', 'latitude',
          'longitude', 'feature class', 'feature code', 'country code', 'cc2',
          'admin1 code', 'admin2 code', 'admin3 code', 'admin4 code',
          'population', 'elevation', 'dem', 'timezone', 'modification date']

reader = csv.DictReader(text_file, fieldnames=fields, delimiter='\t')
# new_mexico = [x for x in reader if x['admin1 code'] == 'NM']

# with open('new_mexico.json', 'w') as export:
#     ujson.dump(new_mexico, export, sort_keys=True, indent=4)

# new_mexico = [x for x in reader if x['admin1 code'] == 'NM']

with open('usa.json', 'w') as export:
    ujson.dump(reader, export, sort_keys=True, indent=4)
