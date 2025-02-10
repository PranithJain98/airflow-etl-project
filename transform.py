import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.dynamicframe import DynamicFrame

glueContext = GlueContext(SparkContext.getOrCreate())
spark = glueContext.spark_session
job = Job(glueContext)

# Load raw data
data_source = glueContext.create_dynamic_frame.from_catalog(
    database="business_db",
    table_name="business_raw_data"
)

# Transformation Logic
transformed_df = data_source.toDF().selectExpr(
    "transaction_id", "timestamp", "customer_id", "product_id", "amount * 1.1 as amount_with_tax"
)

transformed_frame = DynamicFrame.fromDF(transformed_df, glueContext)
glueContext.write_dynamic_frame.from_options(
    frame=transformed_frame,
    connection_type="s3",
    connection_options={"path": "s3://business-processed-data"},
    format="parquet"
)
job.commit()
