# -*- coding: utf-8 -*-

import spacy.en


def create_anno(text, xywh, target, entity, manifest_uri=None):
    '''
    '''
    anno_dict = {}
    anno_dict['@context'] = 'http://www.w3.org/ns/anno.jsonld'
    anno_dict['@type'] = 'Annotation'
    anno_dict['motivation'] = ['tagging', 'commenting']
    comment_dict = {}
    comment_dict['type'] = "TextualBody"
    comment_dict['format'] = 'text/plain'
    comment_dict['value'] = text
    tag_dict = {}
    tag_dict['purpose'] = "tagging"
    tag_dict['value'] = 'entity:' + entity
    anno_dict['body'] = [comment_dict, tag_dict]
    selector_dict = {}
    selector_dict['@type'] = 'FragmentSelector'
    selector_dict['conformsTo'] = "http://www.w3.org/TR/media-frags/"
    selector_dict['value'] = 'xywh=' + xywh
    target_dict = {}
    target_dict['selector'] = selector_dict
    target_dict['source'] = target
    target_dict['type'] = 'SpecificResource'
    if manifest_uri:
        target_dict['dcterms:isPartOf'] = manifest_uri
    anno_dict['target'] = target_dict
    return anno_dict


def box_fitter(list_of_boxes):
    '''
    '''
    pass


def ocr_to_annos(ocr_text, word_index, word_list, canvas_id, manifest_id=None, confidence_thresh=55):
    '''
    Input:
    OCR full text
    Index of words with a list of character positions covered by the word
    List of words with full coordinates and other info
    URI for canvas
    URI for manifest

    Output:
    A list of W3C annotations that can be pushed to a server,
    or written to disk or a database.
    '''
    parser = spacy.en.English()
    parsed = parser(unicode(ocr_text))
    lookup = [x.idx for x in parsed]
    token_index = {}
    resource_list = []
    for token in parsed:
        token_index[token.idx] = [
            [a for a in word_list if a['id'] == x.keys()[0]]
            for x in word_index if token.idx in x.values()[0]]
    for entity in parsed.ents:
        print entity
        print entity.start
        print entity.end
        print token_index[lookup[entity.start]]
        if entity.end - entity.start == 1:
            details = token_index[lookup[entity.start]]
            if (entity.label_ != 'ORDINAL') and (entity.label_ != 'CARDINAL') and details:
                # check the confidence value exceeds a certain threshold?
                # e.g. 75
                confidence = int(details[0][0]['confidence'])
                if confidence > confidence_thresh:
                    resource_list.append(create_anno(entity.text_with_ws.encode('utf-8'),
                                                     details[0][0]['xywh'],
                                                     canvas_id,
                                                     entity.label_,
                                                     manifest_id
                                                     ))
        else:
            for p in range(int(entity.start), int(entity.end)):
                details = token_index[lookup[p]]
                if (entity.label_ != 'ORDINAL') and (entity.label_ != 'CARDINAL') and details:
                    # check the confidence value exceeds a certain threshold?
                    # e.g. 75
                    confidence = int(details[0][0]['confidence'])
                    if confidence > confidence_thresh:
                        resource_list.append(create_anno(entity.text_with_ws.encode('utf-8'),
                                                         details[0][0]['xywh'],
                                                         canvas_id,
                                                         entity.label_,
                                                         manifest_id
                                                         ))
    return resource_list
