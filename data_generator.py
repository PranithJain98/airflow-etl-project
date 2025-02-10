import json
import boto3
import random
from faker import Faker

fake = Faker()
kinesis_client = boto3.client('kinesis', region_name='us-east-1')  # Update with your region
STREAM_NAME = "business-event-stream"

def generate_event():
    return {
        "transaction_id": fake.uuid4(),
        "timestamp": fake.iso8601(),
        "customer_id": random.randint(1000, 9999),
        "product_id": random.randint(100, 500),
        "amount": round(random.uniform(10, 500), 2),
        "payment_method": random.choice(["Credit Card", "Debit Card", "PayPal", "Crypto"]),
        "location": fake.city()
    }

def send_to_kinesis():
    event = generate_event()
    response = kinesis_client.put_record(
        StreamName=STREAM_NAME,
        Data=json.dumps(event),
        PartitionKey=event["transaction_id"]
    )
    print(f"Sent: {event}")

if __name__ == "__main__":
    for _ in range(10):  # Send 10 sample records
        send_to_kinesis()
