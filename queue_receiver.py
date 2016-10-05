import canvas_processor
import boto.sqs
import json


def main():
    conn = boto.sqs.connect_to_region("us-west-2")
    queue = conn.get_queue('ocr1')
    while 1:
        results = queue.get_messages(wait_time_seconds=20, num_messages=5)
        for result in results:
            job = json.loads(result.get_body())
            canvas = job['canvas']
            manifest = job['manifest']
            processed = canvas_processor.CanvasProcess(
                canvas_obj=canvas, manifest_id=manifest)
            queue.delete_message(result)


if __name__ == '__main__':
    main()
