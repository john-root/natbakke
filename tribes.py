from spacy.matcher import Matcher
from spacy.attrs import *
import spacy
#from spacy_basics import initialise_spacy
from spacy.attrs import ORTH, LOWER
from schmentities_refactor import ocr_parse


def main():
    ocr_data = open(
        '/Volumes/IDA-IMAGES/text/M-1011_R-09/M1011R09_0181.hocr').read()
    confidence, typewritten, text = ocr_parse(ocr_data)
    original_parser = spacy.load('en')
    parser = spacy.load('en')
    matcher = Matcher(parser.vocab)
    matcher.add_pattern(
        "narragansett",
        [{LOWER: "narragansett", ORTH: "Narragansett"}],
        label="Narragansett")
    matcher.add_entity(
        "narragansett",  # Entity ID -- Helps you act on the match.
        # Arbitrary attributes (optional)
        {"ent_type": "NORP",
            "wiki_en": "https://en.wikipedia.org/wiki/Narragansett_people"},
        if_exists='update'
    )
    before = original_parser(unicode(text))
    after = parser(unicode(text))
    matches = matcher(after)
    # for ent in before.ents:
    #     print ent.label_
    #     print ent.orth_.encode('utf-8')
    for ent_id, label, start, end in matches:
        entity = matcher.get_entity(ent_id)
        print entity
        print(parser.vocab.strings[ent_id], parser.vocab.strings[
              label], after[start: end].text)

    # parser2.matcher.add_pattern(
    #     "Toadlena",
    #     [

    #         {ORTH: 'Toadlena',
    #          LOWER: 'toadlena'}
    #     ]
    # )
    # parser2.matcher.add_pattern(
    #     "SanJuanAgency",
    #     [

    #         {ORTH: 'San',
    #          LOWER: 'san'},
    #         {ORTH: 'Juan',
    #          LOWER: 'juan'},
    #         {ORTH: 'Agency',
    #          LOWER: 'agency'}
    #     ]
    # )
    # parser2.matcher.add_entity(
    #     "SanJuanAgency",
    #     {"ent_type": "ORG"},
    #     if_exists='update'  # Callback to act on the matches
    # )
    # parser2.matcher.add_entity(
    #     "Toadlena",
    #     {"ent_type": "GPE"},
    #     acceptor=None,  # Accept or modify the match
    #     on_match=None,
    #     if_exists='update'  # Callback to act on the matches
    # )
    # parser2.matcher.add_pattern(
    #     "Toadlena",
    #     [

    #         {ORTH: 'Toadlena',
    #          LOWER: 'toadlena'}
    #     ]
    # )
    # # parser2.matcher.add(
    # #     "false_positives",
    # #     None,
    # #     {},
    # #     [
    # #         [
    # #             {ORTH: 'Diphtheria',
    # #              LOWER: 'diphtheria'}
    # #         ],
    # #         [
    # #             {ORTH: 'Phagocite',
    # #              LOWER: 'phagocite'}
    # #         ]
    # #     ]
    # # )
    # # print example
    # # before = parser(unicode(example))
    # after = parser2(unicode(example))
    # # matches = matcher(after)
    # # for ent_id, label, start, end in matches:
    # #     print(parser2.vocab.strings[ent_id], parser2.vocab.strings[
    # #           label], after[start: end].text)
    # #     entity = matcher.get_entity(ent_id)
    # #     print(entity)
    # for ent in after.ents:
    #     print ent.label_
    #     print ent.orth_.encode('utf-8')
    # # print("Before")
    # # with open('before.csv', 'wb') as f:
    # #     fieldnames = ['Entity_Orth', 'Entity_Label', 'Parts_of_Speech']
    # #     writer = csv.DictWriter(f, fieldnames=fieldnames, dialect='excel')
    # #     writer.writeheader()
    # #     for ent in before.ents:
    # #         if ent.label_ not in ['TIME', 'PERCENT', 'CARDINAL', 'ORDINAL', 'QUANTITY', 'MONEY'] and len(ent.orth_) > 3:
    # #             writer.writerow({'Entity_Orth': ent.orth_.encode('utf-8'),
    # #                              'Entity_Label': ent.label_,
    # #                              'Parts_of_Speech': ' '.join([w.tag_ for w in ent])})
    # # print("After")
    # # with open('after_new.csv', 'wb') as f:
    # #     fieldnames = ['Entity_Orth', 'Entity_Label', 'Parts_of_Speech']
    # #     writer = csv.DictWriter(f, fieldnames=fieldnames, dialect='excel')
    # #     writer.writeheader()
    # #     for ent in after.ents:
    # #         if ent.label_ not in ['TIME', 'PERCENT', 'CARDINAL', 'ORDINAL', 'QUANTITY', 'MONEY'] and len(ent.orth_) > 3:
    # #             writer.writerow({'Entity_Orth': ent.orth_.encode('utf-8'),
    # #                              'Entity_Label': ent.label_,
    # #                              'Parts_of_Speech': ' '.join([w.tag_ for w in ent])})


if __name__ == '__main__':
    main()
