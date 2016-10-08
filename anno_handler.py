from pyld import jsonld

'''
Serialise and context handling for annos.
'''

w3c_context = 'https://www.w3.org/ns/anno.jsonld'
oa_context = ''
iiif_context = ''


def create_anno(text, xywh, target, tag=None, manifest_uri=None):
    '''
    Works OK with expansion/compaction using the w3c_context,
    but OA context and IIIF context not Mirador compatible.

    Need: oa:Tag, and cnts: chars

    NB: need to add SVG paths as well as xywh.

    Plus error handling for empty target, text, etc.
    '''
    anno_dict = {}
    anno_dict['@type'] = 'oa:Annotation'
    anno_dict['oa:motivatedBy'] = ['oa:tagging', 'oa:commenting']
    comment_dict = {}
    if text:
        comment_dict['type'] = "oa:TextualBody"
        comment_dict['dc:format'] = 'text/plain'
        comment_dict['rdf:value'] = text
    tag_dict = {}
    if tag:
        tag_dict['oa:hasPurpose'] = "oa:tagging"
        tag_dict['rdf:value'] = 'entity:' + tag
    selector_dict = {}
    if xywh:
        selector_dict['@type'] = 'oa:FragmentSelector'
        selector_dict['dcterms:conformsTo'] = "http://www.w3.org/TR/media-frags/"
        selector_dict['rdf:value'] = 'xywh=' + xywh
    target_dict = {}
    if target:
        if selector_dict:
            target_dict['oa:hasSelector'] = selector_dict
        target_dict['oa:hasSource'] = target
        target_dict['type'] = 'oa:SpecificResource'
        if manifest_uri:
            target_dict['dcterms:isPartOf'] = manifest_uri
        anno_dict['oa:hasTarget'] = target_dict
    # should this always return a list?
    body_list = []
    motivation_list = []
    if comment_dict:
        body_list.append(comment_dict)
        motivation_list.append('oa:commenting')
    if tag_dict:
        body_list.append(tag_dict)
        motivation_list.append('oa:tagging')
    if body_list and anno_dict['oa:hasTarget']:
        if len(body_list) == 1:
            anno_dict['oa:hasBody'] = body_list[0]
            anno_dict['oa:motivatedBy'] = motivation_list[0]
        elif len(body_list) > 1:
            anno_dict['oa:hasBody'] = body_list
            anno_dict['oa:motivatedBy'] = motivation_list
        else:
            print 'Error handling body'
        return anno_dict
    else:
        return None


def anno_create():
    pass


def anno_expand():
    pass


def anno_compact():
    pass
