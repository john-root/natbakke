# from spacy.matcher import Matcher
# from spacy.attrs import *
# import spacy
# from spacy_basics import initialise_spacy
# from spacy.attrs import ORTH, LOWER
from schmentities_refactor import ocr_parse
from tribes_import import initialise_tribes
import glob

def main():
    csv_file = '/Users/matt.mcgrattan/Documents/tribe_names.csv'
    matcher, parser = initialise_tribes(csv_file)
    ocr = glob.glob('/Volumes/IDA-IMAGES/text/M-1011_R-09/*.hocr')
    for ocr_file in ocr:
        ocr_data = open(ocr_file).read()
        confidence, typewritten, text = ocr_parse(ocr_data)
        # matcher, parser =initialise_spacy('new_mexico.json')
        # matcher, parser =initialise_spacy()
        # parser = spacy.load('en')
        '''
        Create a custom matcher.

        Final output will need to redact
        any entities in the non-custom matcher
        and replace with custom entities where they
        exist.
        '''
        # matcher = Matcher(parser.vocab)
        # add a pattern (or patterns)
        # matcher.add_pattern(
        #     "narragansett",
        #     [{LOWER: "narragansett", ORTH: "Narragansett"}],
        #     label="Narragansett")
        # matcher.add_entity(
        #     "narragansett",  # Entity ID -- Helps you act on the match.
        #     # Arbitrary attributes (optional)
        #     {"ent_type": "TRIBE",
        #         "wiki_en": "https://en.wikipedia.org/wiki/Narragansett_people"},
        #     if_exists='update'
        # )
        # matcher.add_pattern(
        #     "courdalene",
        #     [{LOWER: "cour", ORTH: "Cour"}, {LOWER: "d'alene", ORTH: "D'Alene"}],
        #     label="Coeur d'Alene")
        # matcher.add_pattern(
        #     "courdalene",
        #     [{LOWER: "coeur", ORTH: "Coeur"}, {LOWER: "d'alene", ORTH: "d'Alene"}],
        #     label="Coeur d'Alene")
        # matcher.add_entity(
        #     "courdalene",  # Entity ID -- Helps you act on the match.
        #     # Arbitrary attributes (optional)
        #     {"ent_type": "TRIBE",
        #         "wiki_en": "https://en.wikipedia.org/wiki/Coeur_d%27Alene_people"},
        #     if_exists='update'
        # )
        # before = original_parser(unicode(text))
        # for ent in before.ents:
        #     print ent.label_
        #     print ent.orth_.encode('utf-8')
        after = parser(unicode(text))
        matches = matcher(after)
        for ent_id, label, start, end in matches:
            '''
            Grab the dict from the entity
            '''
            entity = matcher.get_entity(ent_id)
            label = parser.vocab.strings[label]
            entity_id = parser.vocab.strings[ent_id]
            ent_type = entity["ent_type"]
            print label
            print ent_type
            # print 'Start offset: %s' % start
            # print 'End offset: %s' % end
            # print 'Text in the data: %s' % after[start: end].text
            '''
            Entity id, label (for entity), string matched in the text
            '''
            # print(parser.vocab.strings[ent_id], parser.vocab.strings[
            #       label], after[start: end].text)


if __name__ == '__main__':
    main()
