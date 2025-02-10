import json
import boto3

s3_client = boto3.client('s3')
kinesis_client = boto3.client('kinesis')

BUCKET_NAME = "business-raw-data-bucket"
STREAM_NAME = "business-event-stream"

def lambda_handler(event, context):
    for record in event['Records']:
        payload = record["kinesis"]["data"]
        data = json.loads(payload)
        file_name = f"raw-data/{data['transaction_id']}.json"
        
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body=json.dumps(data)
        )
        print(f"Stored in S3: {file_name}")

    return {"statusCode": 200, "body": "Success"}
