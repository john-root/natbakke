from spacy_basics import initialise_spacy
import ftfy
import csv
import glob



def main():
    foo = glob.glob('/Users/matt.mcgrattan/Documents/IDA-NARA_files/M-1473_R-09/*.txt')
    parser = initialise_spacy()
    # print example
    print("Working")
    with open('output.csv', 'wb') as f:
        fieldnames = ['Entity_Orth', 'Entity_Label', 'Source']
        writer = csv.DictWriter(f, fieldnames=fieldnames, dialect='excel')
        writer.writeheader()
        for bar in foo:
            print bar
            example = ftfy.fix_text(
                (open(bar).read().decode('utf-8')))
            thing = parser(unicode(example))
            for ent in thing.ents:
                print ent
                if ent.label_ not in ['TIME', 'PERCENT', 'CARDINAL', 'ORDINAL', 'QUANTITY', 'MONEY'] and len(ent.orth_) > 3:
                    writer.writerow({'Entity_Orth': ent.orth_.encode('utf-8'),
                                     'Entity_Label': ent.label_,
                                     'Source': bar})


if __name__ == '__main__':
    main()
