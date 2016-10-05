import boto.sqs
import canvas_processor
import json
from boto.sqs.message import RawMessage


def main():
    conn = boto.sqs.connect_to_region("us-west-2")
    queue = conn.get_queue('ocr1')
    item = canvas_processor.Manifest(
        uri='https://tomcrane.github.io/scratch/manifests/ida/m1011-santa-fe-1910-30.json')
    # for canvas in item.canvases:
    msg = {}
    msg['manifest'] = item.requested.uri
    msg['canvas'] = item.canvases[0] # canvas
    m = RawMessage()
    m.set_body(json.dumps(msg, indent=4))
    status = queue.write(m)



if __name__ == '__main__':
    main()

