from pyld import jsonld

'''
Serialise and context handling for annos.
'''

w3c_context = 'https://www.w3.org/ns/anno.jsonld'
oa_context = ''
iiif_context = ''

def create_anno(text, xywh, target, entity, manifest_uri=None):
    '''
    Works OK with expansion/compaction using the w3c_context,
    but OA context and IIIF context not Mirador compatible.

    Need: oa:Tag, and cnts: chars
    '''
    anno_dict = {}
    # anno_dict['@context'] = 'http://www.w3.org/ns/anno.jsonld'
    anno_dict['@type'] = 'oa:Annotation'
    anno_dict['oa:motivatedBy'] = ['oa:tagging', 'oa:commenting']
    comment_dict = {}
    comment_dict['type'] = "oa:TextualBody"
    comment_dict['dc:format'] = 'text/plain'
    comment_dict['rdf:value'] = text
    tag_dict = {}
    tag_dict['oa:hasPurpose'] = "oa:tagging"
    tag_dict['rdf:value'] = 'entity:' + entity
    anno_dict['oa:hasBody'] = [comment_dict, tag_dict]
    selector_dict = {}
    selector_dict['@type'] = 'oa:FragmentSelector'
    selector_dict['dcterms:conformsTo'] = "http://www.w3.org/TR/media-frags/"
    selector_dict['rdf:value'] = 'xywh=' + xywh
    target_dict = {}
    target_dict['oa:hasSelector'] = selector_dict
    target_dict['oa:hasSource'] = target
    target_dict['type'] = 'oa:SpecificResource'
    if manifest_uri:
        target_dict['dcterms:isPartOf'] = manifest_uri
    anno_dict['oa:hasTarget'] = target_dict
    return anno_dict


def anno_create():
    pass


def anno_expand():
    pass


def anno_compact():
    pass

