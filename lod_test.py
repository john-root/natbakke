from spacy_basics import initialise_spacy
import ftfy


def main():
    example = ftfy.fix_text(open('./data/e4488a6cb20ed47e2050daf5e54a9831.txt').read())
    parser = initialise_spacy('new_mexico.json', geonames=True)
    parser2 = initialise_spacy()
    print example
    # before = parser(unicode(example))
    # after = parser2(unicode(example))
    # print("Before")
    # for ent in before.ents:
    #     print(ent.text, ent.label_, [w.tag_ for w in ent])
    # print("After")
    # for ent in after.ents:
    #     print(ent.text, ent.label_, [w.tag_ for w in ent])



if __name__ == '__main__':
    main()