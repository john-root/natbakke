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
    manifest_queue = conn.get_queue('ocr0')
    canvas_queue = conn.get_queue('ocr1')
    while 1:
        manifest_results = manifest_queue.get_messages(wait_time_seconds=20,
                                                       num_messages=5)
        for manifest_result in manifest_results:
            job = json.loads(manifest_result.get_body())
            manifest_uri = job['manifest']
            canvases_enqueue(canvas_queue, manifest_uri)
            manifest_queue.delete_message(manifest_result)


if __name__ == '__main__':
    main()
