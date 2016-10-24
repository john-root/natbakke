from spacy_basics import initialise_spacy
import ftfy
from spacy.attrs import ORTH, LOWER
import csv


def main():
    example = ftfy.fix_text(
        (open('./test2.txt').read().decode('utf-8')))
    parser = initialise_spacy('new_mexico.json', geonames=True)
    parser = initialise_spacy()
    parser.matcher.add(
        "Toadlena",
        "GPE",
        {},
        [
            [
                {ORTH: 'Toadlena',
                 LOWER: 'toadlena'}
            ]
        ]
    )
    parser.matcher.add(
        "ToadlenaSchool",
        "ORG",
        {},
        [
            [
                {ORTH: 'Toadlena',
                 LOWER: 'toadlena'},
                {ORTH: 'School',
                 LOWER: 'school'}
            ]
        ]
    )
    parser.matcher.add(
        "SanJuanSchool",
        "ORG",
        {},
        [
            [
                {ORTH: 'San',
                 LOWER: 'san'},
                {ORTH: 'Juan',
                 LOWER: 'juan'},
                {ORTH: 'School',
                 LOWER: 'school'}
            ]
        ]
    )
    parser.matcher.add(
        "SanJuanSAgency",
        "ORG",
        {},
        [
            [
                {ORTH: 'San',
                 LOWER: 'san'},
                {ORTH: 'Juan',
                 LOWER: 'juan'},
                {ORTH: 'Agency',
                 LOWER: 'agency'}
            ]
        ]
    )
    parser.matcher.add(
        "false_positives",
        None,
        {},
        [
            [
                {ORTH: 'Diphtheria',
                 LOWER: 'diphtheria'}
            ]
        ]
    )
    parser2 = initialise_spacy()
    # print example
    before = parser2(unicode(example))
    after = parser(unicode(example))
    print("Before")
    with open('before.csv', 'wb') as f:
        fieldnames = ['Entity_Orth', 'Entity_Label', 'Parts_of_Speech']
        writer = csv.DictWriter(f, fieldnames=fieldnames, dialect='excel')
        writer.writeheader()
        for ent in before.ents:
            if ent.label_ not in ['TIME', 'PERCENT', 'CARDINAL', 'ORDINAL', 'QUANTITY', 'MONEY'] and len(ent.orth_) > 3:
                writer.writerow({'Entity_Orth': ent.orth_.encode('utf-8'),
                                 'Entity_Label': ent.label_,
                                 'Parts_of_Speech': ' '.join([w.tag_ for w in ent])})
    print("After")
    with open('after4.csv', 'wb') as f:
        fieldnames = ['Entity_Orth', 'Entity_Label', 'Parts_of_Speech']
        writer = csv.DictWriter(f, fieldnames=fieldnames, dialect='excel')
        writer.writeheader()
        for ent in after.ents:
            if ent.label_ not in ['TIME', 'PERCENT', 'CARDINAL', 'ORDINAL', 'QUANTITY', 'MONEY'] and len(ent.orth_) > 3:
                writer.writerow({'Entity_Orth': ent.orth_.encode('utf-8'),
                                 'Entity_Label': ent.label_,
                                 'Parts_of_Speech': ' '.join([w.tag_ for w in ent])})


if __name__ == '__main__':
    main()
