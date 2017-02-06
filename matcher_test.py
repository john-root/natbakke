from __future__ import unicode_literals, print_function

import spacy.en
import spacy.matcher
from spacy.attrs import ORTH, TAG, LOWER, IS_ALPHA, FLAG63

# import plac


def main():
    nlp = spacy.en.English()
    example = u"I grew up in San Ildefonso Pueblo, and have never been to Tottenham Lane."
    before = nlp(example)
    print("Before")
    for ent in before.ents:
        print(ent.text, ent.label_, [w.tag_ for w in ent])
    # Output:
    # Google ORG [u'NNP']
    # google ORG [u'VB']
    # google ORG [u'NNP']
    nlp.matcher.add(
        "TottenhamLane",  # Entity ID: Not really used at the moment.
        "GPE",   # Entity type: should be one of the types in the NER data
        {"wiki_en": "Google_Now"},  # Arbitrary attributes. Currently unused.
        [  # List of patterns that can be Surface Forms of the entity

            # This Surface Form matches "Google Now", verbatim
            [  # Each Surface Form is a list of Token Specifiers.
                {  # This Token Specifier matches tokens whose orth field is "Google"
                    ORTH: "Tottenham",
                    LOWER: "tottenham"
                },
                {  # This Token Specifier matches tokens whose orth field is "Now"
                    ORTH: "Lane",
                    LOWER: "lane"
                }
            ]
        ]
    )
    after = nlp(example)
    print("After")
    for ent in after.ents:
        print(ent.text, ent.label_, [w.tag_ for w in ent])


if __name__ == '__main__':
    main()
