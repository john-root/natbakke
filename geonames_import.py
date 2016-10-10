# -*- coding: utf-8 -*-
import csv
import sys
csv.field_size_limit(sys.maxsize)
import ujson


foo = open('US.txt')

fields = ['geonameid', 'name', 'asciiname', 'alternatenames', 'latitude', 'longitude', 'feature class', 'feature code', 'country code', 'cc2',
          'admin1 code', 'admin2 code', 'admin3 code', 'admin4 code', 'population', 'elevation', 'dem', 'timezone', 'modification date']

reader = csv.DictReader(foo, fieldnames=fields, delimiter='\t')
new_mexico = [x for x in reader if x['admin1 code'] == 'NM']

# alternates = [y for y in new_mexico if y['alternatenames'] != '']

with open('new_mexico.json', 'w') as export:
	ujson.dump(new_mexico, export, sort_keys=True, indent=4)