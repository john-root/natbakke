from spacy_basics import initialise_spacy
import ftfy
from spacy.attrs import ORTH, LOWER


def main():
    example = ftfy.fix_text(
        (open('./data/4d1335b1a2e93cbda27c54638419d073.txt').read().decode('utf-8')))
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
        ])
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
