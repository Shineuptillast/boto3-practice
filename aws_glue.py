import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from pyspark.sql.functions import func
from pyspark.sql.types import LongType
import os
# @params: [JOB_NAME]

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
bucket_name = "aws-data-pipeline-storage-layer"
dynamo_db_table = "financial_complaint"
bucket_url = f"s3://{bucket_name}/inbox/*.json"


sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

"""df_glue = glueContext.create_dynamic_frame_from_options(
    connection_type='s3', connection_options={"paths": [s3_location]}, format='json', tranformation_ctx='data_1')"""
df_spark = spark.read.json(bucket_url)

df_spark = df_spark.withColumn(
    "complaint_id", func.col("complaint_id").cast(LongType()))

df_spark.columns
df_spark.count()
df_spark.show(5, truncate=False)

df_glue = glueContext.create_dynamic_frame.from_options(connection_type='dynamodb',
                                                        connection_options={
                                                            "dynamodb.input.tableName": dynamo_db_table,
                                                            "dynamo.throughput.read.percent": '1.0',
                                                            'dynamodb.splits': "100"
                                                        })
df_dynamo = df_glue.toDF()
df_dynamo_existing = df_dynamo.select('complaint_id').withColumnRenamed(
    'complaint_id', 'existing_complaint_id')
if df_dynamo_existing.count() != 0:
    new_df = df_spark.join(
        df_dynamo_existing, df_spark['complaint_id'] == df_dynamo['existing_complaint_id'], "left")
    dyf = new_df.filter("existing_complaint_id id null")
    df_1 = dyf.drop('existing_complaint_id')
    df2 = DynamicFrame.fromDF(df_1, glueContext, "df2")

    glueContext.write_dynamic_frame_from_options(
        frame=df2,
        connection_type="dynamodb",
        connection_options={
            "dynamodb.input.tableName": dynamo_db_table,
            "dynamo.throughput.read.percent": '1.0',
            'dynamodb.splits': "100"
        },
        transformation_ctx="datasink")

else:
    df_4 = DynamicFrame.fromDF(df_spark, glueContext, "df_4")
    glueContext.write_dynamic_frame_from_options(
        frame=df_4,
        connection_type="dynamodb",
        connection_options={
            "dynamodb.input.tableName": dynamo_db_table,
            "dynamo.throughput.read.percent": '1.0',
            'dynamodb.splits': "100"
        },
        transformation_ctx="datasink_1")

os.system(f"aws s3 sync s3://{bucket_name}/inbox s3://{bucket_name}/archive")

os.system(f"aws s3 rm s3://{bucket_name}/inbox/*.json --recursive")


job.commit()
