import csv
import sys
csv.field_size_limit(sys.maxsize)


foo = open('US.txt')

fields = ['geonameid', 'name', 'asciiname', 'alternatenames', 'latitude', 'longitude', 'feature class', 'feature code', 'country code', 'cc2',
          'admin1 code', 'admin2 code', 'admin3 code', 'admin4 code', 'population', 'elevation', 'dem', 'timezone', 'modification date']

reader = csv.DictReader(foo, fieldnames=fields, delimiter='\t') #dialect='tab')
new_mexico = [x for x in reader if x['admin1 code'] == 'NM']

print new_mexico