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


def ocr_to_annos(entity_parser, ocr_text, word_index,
                 word_list, canvas_id,
                 manifest_id=None,
                 confidence_thresh=55):
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

    Needs box joining for multi-token annos on the same line.
    '''
    # parser = spacy.en.English()
    parser = entity_parser
    parsed = parser(unicode(ocr_text))
    lookup = [x.idx for x in parsed]
    token_index = {}
    resource_list = []
    # Build an index of tokens with details from OCR
    for token in parsed:
        token_index[token.idx] = [
            [a for a in word_list if a['id'] == x.keys()[0]]
            for x in word_index if token.idx in x.values()[0]]
    # Extract entities and step through them
    for entity in parsed.ents:
        # print entity
        # print entity.start
        # print entity.end
        # print token_index[lookup[entity.start]]
        if entity.end - entity.start == 1:
            try:
                details = token_index[lookup[entity.start]][0][0]
            except IndexError:
                # print 'No details'
                details = None
            if details:
                if 'confidence' in details:
                    confidence = details['confidence']
                else:
                    confidence = None
            if ((entity.label_ != 'ORDINAL') and
                    (entity.label_ != 'CARDINAL') and
                    details):
                candidate_anno = create_anno(
                    entity.orth_.encode('utf-8'),
                    details['xywh'],
                    canvas_id,
                    entity.label_,
                    manifest_id
                )
                if confidence:
                    if confidence > confidence_thresh:
                        resource_list.append(candidate_anno)
                    else:
                        print 'OCR confidence too low.'
                else:  # if no confidence value, just go ahead and append.
                    resource_list.append(candidate_anno)
        # multi word/token entity
        # needs revision to handle occasional 'drift' of anno box placement
        else:
            for p in range(int(entity.start), int(entity.end)):
                try:
                    details = token_index[lookup[p]][0][0]
                except IndexError:
                    # print 'No details'
                    details = None
                if details:
                    if 'confidence' in details:
                        confidence = details['confidence']
                    else:
                        confidence = None
                if ((entity.label_ != 'ORDINAL') and
                        (entity.label_ != 'CARDINAL') and
                        details):
                    candidate_anno = create_anno(
                        entity.orth_.encode('utf-8'),
                        details['xywh'],
                        canvas_id,
                        entity.label_,
                        manifest_id
                    )
                    if confidence:
                        if confidence > confidence_thresh:
                            resource_list.append(candidate_anno)
                        else:
                            print 'OCR confidence too low.'
                    else:  # if no confidence value, just go ahead and append.
                        resource_list.append(candidate_anno)
    return resource_list
