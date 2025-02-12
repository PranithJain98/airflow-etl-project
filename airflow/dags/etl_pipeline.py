from airflow import DAG
from airflow.providers.amazon.aws.operators.s3 import S3CreateBucketOperator, S3FileTransformOperator
from airflow.providers.amazon.aws.operators.redshift_data import RedshiftDataOperator
from datetime import datetime
import boto3

AWS_CONN_ID = "aws_default"
BUCKET_NAME = "business-processed-data"
REDSHIFT_CLUSTER_ID = "business-cluster"
REDSHIFT_DB = "dev"
REDSHIFT_USER = "admin"
IAM_ROLE_ARN = "arn:aws:iam::605134444022:role/RedshiftS3AccessRole"
S3_FILE_KEY = "transformed_data.parquet"

# Function to check if the S3 bucket exists
def check_s3_bucket_exists():
    s3 = boto3.client("s3")
    response = s3.list_buckets()
    for bucket in response["Buckets"]:
        if bucket["Name"] == BUCKET_NAME:
            return True
    return False

# Function to create the bucket if it does not exist
def create_s3_bucket():
    s3 = boto3.client("s3")
    if not check_s3_bucket_exists():
        s3.create_bucket(Bucket=BUCKET_NAME)
        print(f"S3 Bucket {BUCKET_NAME} created successfully.")

# Define the DAG
default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 2, 9),
    "retries": 1,
}

dag = DAG(
    dag_id="etl_pipeline_s3_redshift",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False
)

# Task 1: Create S3 Bucket (if it does not exist)
create_s3_bucket_task = S3CreateBucketOperator(
    task_id="create_s3_bucket",
    bucket_name=BUCKET_NAME,
    aws_conn_id=AWS_CONN_ID,
    region_name="us-east-1",
    dag=dag
)

# Task 2: Upload Processed Data to S3
upload_to_s3_task = S3FileTransformOperator(
    task_id="upload_transformed_data",
    source_s3_key="/path/to/local/transformed_data.parquet",
    dest_s3_key=f"s3://{BUCKET_NAME}/{S3_FILE_KEY}",
    replace=True,
    dag=dag
)


# Task 3: Load Data from S3 to Redshift
copy_to_redshift_task = RedshiftDataOperator(
    task_id="copy_data_to_redshift",
    cluster_identifier=REDSHIFT_CLUSTER_ID,
    database=REDSHIFT_DB,
    db_user=REDSHIFT_USER,
    sql=f"""
    COPY business_data
    FROM 's3://{BUCKET_NAME}/{S3_FILE_KEY}'
    IAM_ROLE '{IAM_ROLE_ARN}'
    FORMAT AS PARQUET;
    """,
    aws_conn_id=AWS_CONN_ID,
    dag=dag
)

# Define task dependencies
create_s3_bucket_task >> upload_to_s3_task >> copy_to_redshift_task
