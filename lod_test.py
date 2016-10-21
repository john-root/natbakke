from spacy_basics import initialise_spacy
import ftfy
from spacy.attrs import ORTH, LOWER


def main():
    example = ftfy.fix_text(
        (open('./test.txt').read().decode('utf-8')))
    parser = initialise_spacy('new_mexico.json', geonames=True)
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
    parser2 = initialise_spacy()
    print example
    before = parser2(unicode(example))
    after = parser(unicode(example))
    print("Before")
    for ent in before.ents:
        print(ent.text, ent.label_, [w.tag_ for w in ent])
    print("After")
    for ent in after.ents:
        print(ent.text, ent.label_, [w.tag_ for w in ent])


if __name__ == '__main__':
    main()
