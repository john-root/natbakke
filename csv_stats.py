import csv
from collections import Counter
import operator
import json


csv_file = 'output_1.csv'
# source = open(csv_file).read()


reader = csv.DictReader(open(csv_file))

orths = []
rows = []
for row in reader:
    orths.append(row['Entity_Orth'])
    rows.append(row)

unique_orths = set(orths)

c = Counter(orths)
stats = {}
for item in c.items():
    z = list(item)
    stats[str(z[0])] = z[1]
    # if z[1] > 1:
    #     print 'Common: %s' % z



sorted_stats = reversed(sorted(stats.items(), key=operator.itemgetter(1)))
big_list = []
for stat in sorted_stats:
    stat_dict = {}
    stat_dict['Entity'] = list(stat)[0]
    stat_dict['Count'] = list(stat)[1]
    stat_dict['Sources']= list(set([x['Source'] for x in rows if x['Entity_Orth'] == stat_dict['Entity']]))
    stat_dict['Type']= list(set([x['Entity_Label'] for x in rows if x['Entity_Orth'] == stat_dict['Entity']]))
    big_list.append(stat_dict)

with open('stats_1a.json', 'w') as outfile:
    json.dump(big_list, outfile, indent=4, sort_keys=True)
# print json.dumps(big_list, indent=4)



