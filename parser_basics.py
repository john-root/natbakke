# -*- coding: utf-8 -*-

import spacy.en


def ocr_to_annos(ocr_text, word_index, word_list):
    parser = spacy.en.English()
    parsed = parser(unicode(ocr_text))
    lookup = [x.idx for x in parsed]
    token_index = {}
    for token in parsed:
        token_index[token.idx] = [
            [a for a in word_list if a['id'] == x.keys()[0]]
            for x in word_index if token.idx in x.values()[0]]
    for entity in parsed.ents:
        for p in range(int(entity.start), int(entity.end)):
            details = token_index[lookup[p]]
            print entity.text_with_ws
            print details
