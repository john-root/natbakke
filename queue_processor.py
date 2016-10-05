import boto.sqs
import canvas_processor
import json


def main():
    conn = boto.sqs.connect_to_region("us-west-2")
    queue = conn.get_queue('ocr1')
    item = canvas_processor.Manifest(
        uri='https://tomcrane.github.io/scratch/manifests/ida/m1011-santa-fe-1910-30.json')
    for canvas in item.canvases:
        canvas_json = json.dumps(canvas)
        print canvas_json
        print item.requested.uri



if __name__ == '__main__':
    main()

