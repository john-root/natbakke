import flask
from flask import request
import boto.sqs
import json
from boto.sqs.message import RawMessage
import urllib


def manifest_enqueue(manifest_uri):
    conn = boto.sqs.connect_to_region("us-west-2")
    manifest_queue = conn.get_queue('ocr0')
    msg = {}
    msg['manifest'] = manifest_uri
    m = RawMessage()
    m.set_body(json.dumps(msg, indent=4))
    manifest_queue.write(m)


app = flask.Flask(__name__)
@app.route('/queue_manifest', methods=['GET', 'POST'])
def manifestor():
    manifest = urllib.unquote_plus(request.args.get('manifest'))
    manifest_enqueue(manifest)
    content = 'Queued: %s' % manifest
    resp = flask.Response(content)
    return resp

