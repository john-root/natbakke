import canvas_processor
import boto.sqs
import json


def main():
    conn = boto.sqs.connect_to_region("us-west-2")
    queue = conn.get_queue('ocr1')
    results = queue.get_messages()
    for result in results:
        job = json.loads(result.get_body())
        print job['canvas']
        print job['manifest']
        # processed = canvas_processor.CanvasProcess(
        #     canvas_obj=canvas, manifest_id=item.requested.uri)



if __name__ == '__main__':
    main()
