from spacy_basics import initialise_spacy
import ftfy
import csv
import glob
from collections import Counter


def main():
    big_list = []
    foo = glob.glob(
        '/Users/matt.mcgrattan/Documents/IDA-NARA_files/M-1473_R-09/*.txt')
    parser = initialise_spacy()
    # print example
    # print("Working")
    with open('output.csv', 'wb') as f:
        fieldnames = ['Entity_Orth', 'Entity_Label', 'Source']
        writer = csv.DictWriter(f, fieldnames=fieldnames, dialect='excel')
        writer.writeheader()
        for bar in foo:
            #print bar
            example = ftfy.fix_text(
                (open(bar).read().decode('utf-8')))
            thing = parser(unicode(example))
            for ent in thing.ents:
                if ent.label_ not in ['TIME', 'PERCENT', 'CARDINAL', 'ORDINAL', 'QUANTITY', 'MONEY'] and len(ent.orth_) > 3:
                    cont_row = {'Entity_Orth': ent.orth_.encode('utf-8'),
                                'Entity_Label': ent.label_,
                                'Source': bar}
                    big_list.append(ent.orth_.encode('utf-8'))
                    writer.writerow(cont_row)
    #print big_list
    c = Counter( big_list )
    for item in c.items():
        z = list(item)
        print str(z[0]) + ',' + str(z[1])



if __name__ == '__main__':
    main()
