import flask
from flask import request
import boto.sqs
import json
from boto.sqs.message import RawMessage


def manifest_enqueue():
    conn = boto.sqs.connect_to_region("us-west-2")
    manifest_queue = conn.get_queue('ocr0')
    msg = {}
    msg['manifest'] = 'https://tomcrane.github.io/scratch/manifests/ida/m1011-santa-fe-1910-30.json'
    m = RawMessage()
    m.set_body(json.dumps(msg, indent=4))
    manifest_queue.write(m)


app = flask.Flask(__name__)
@app.route('/queue_manifest', methods=['POST'])
def manifestor():
    manifest = request.args.get('manifest')
    print manifest
