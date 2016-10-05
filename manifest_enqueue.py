import boto.sqs
import json
from boto.sqs.message import RawMessage


def main():
    conn = boto.sqs.connect_to_region("us-west-2")
    manifest_queue = conn.get_queue('ocr0')
    msg = {}
    msg['manifest'] = 'https://tomcrane.github.io/scratch/manifests/ida/m1011-santa-fe-1910-30.json'
    m = RawMessage()
    m.set_body(json.dumps(msg, indent=4))
    manifest_queue.write(m)


if __name__ == '__main__':
    main()
