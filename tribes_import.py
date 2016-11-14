import csv
import spacy.en
import spacy.matcher
from spacy.attrs import ORTH, LOWER
# import json

def initialise_tribes(csv_file):
    '''

    '''
    reader = csv.DictReader(open(csv_file))
    parser = spacy.en.English()
    matcher = spacy.matcher.Matcher(parser.vocab)
    names = []
    for row in reader:
        # master name for the tribe
        name = row['Tribe'].strip()
        names.append(name)
        '''
        Add the various alternative forms.
        '''
        alt_forms = []
        if row['Prefix']:
            alt_forms.append(
                ' '.join([row['Prefix'].strip(), row['Tribe'].strip()]))
            if 'pueblo' in row['Prefix'].lower():
                alt_forms.append(' '.join([row['Tribe'].strip(), 'Pueblo']))
        if row['Variant Names']:
            if ';' in row['Variant Names']:
                for variant in row['Variant Names'].split(';'):
                    alt_forms.append(variant.strip())
            else:
                alt_forms.append(row['Variant Names'].strip())
        id = ''.join(name.split())
        name_tokens = name.split()
        word_list = []
        for token in name_tokens:
            word_dict = {LOWER: token.strip().lower(), ORTH: token.strip()}
            word_list.append(word_dict)
        matcher.add_pattern(
            ''.join(name.split()).lower(),
            word_list,
            label=name)
        add_pat = [''.join(name.split()).lower(), word_list, {"label": name}]
        # print json.dumps(add_pat, indent=4)
        for alt_form in alt_forms:
            names.append(alt_form)
            word_list = []
            for token in alt_form.split():
                word_dict = {LOWER: token.strip().lower(), ORTH: token.strip()}
                word_list.append(word_dict)
            matcher.add_pattern(
                ''.join(name.split()).lower(),
                word_list,
                label=name)
            add_pat = [''.join(name.split()).lower(), word_list, {"label": name}]
            # print json.dumps(add_pat, indent=4)
        matcher.add_entity(
            # Entity ID -- Helps you act on the match.
            ''.join(name.split()).lower(),
            # Arbitrary attributes (optional)
            {"ent_type": "TRIBE",
             "loc_id": row['Source or LOC Linked Data Identifier'].strip()},
            if_exists='update'
        )
    txt = open('tribe_list2.txt').read()
    new_tribes = []
    for line in txt.split('\n'):
        additional_tribe = line.split('\t')[0]
        if additional_tribe not in names:
            new_tribes.append(additional_tribe)
    for new_tribe in new_tribes:
        word_list = []
        for token in new_tribe.split():
            word_dict = {LOWER: token.strip().lower(), ORTH: token.strip()}
            word_list.append(word_dict)
        matcher.add_pattern(
            ''.join(new_tribe.split()).lower(),
            word_list,
            label=new_tribe)
        matcher.add_entity(
            # Entity ID -- Helps you act on the match.
            ''.join(new_tribe.split()).lower(),
            # Arbitrary attributes (optional)
            {"ent_type": "TRIBE",
             "loc_id": ""},
            if_exists='update'
        )
    return matcher, parser
