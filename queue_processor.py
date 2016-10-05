import boto.sqs
import canvas_processor
import json
from boto.sqs.message import RawMessage

def canvases_enqueue(queue, manifest_uri):
    item = canvas_processor.Manifest(manifest_uri)
    for canvas in item.canvases:
        msg = {}
        msg['manifest'] = item.requested.uri
        msg['canvas'] = canvas
        m = RawMessage()
        m.set_body(json.dumps(msg, indent=4))
        queue.write(m)


def main():
    conn = boto.sqs.connect_to_region("us-west-2")
    queue = conn.get_queue('ocr1')
    canvases_enqueue(queue, manifest_uri='https://tomcrane.github.io/scratch/manifests/ida/m1011-santa-fe-1910-30.json')



if __name__ == '__main__':
    main()

