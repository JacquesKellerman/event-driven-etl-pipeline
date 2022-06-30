import boto3
import json
import logging
import os
import psycopg2

import etl_data_functions
import db_functions

# Initialize boto3 clients for Parameter Store and SNS
sns_client = boto3.client('sns')
ssm_client = boto3.client('ssm')

# # Get DB configuration from Parameter store
country_name = ssm_client.get_parameter(Name='/Covid19DataETL/country/name')

url_nyt = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us.csv"
url_jh = "https://raw.githubusercontent.com/datasets/covid-19/master/data/time-series-19-covid-combined.csv"

# Setup logging to CloudWatch
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)

# Notify via SNS
def notifyViaSNS(text):
    try:
        sns_client.publish(TopicArn=os.environ['SNS_TOPIC'], Subject = 'Covid19 ETL Summary', Message = json.dumps({'default': json.dumps(text)}), MessageStructure = 'json')
    except Exception as e:
        logger.error("SNS send notification failed: {}".format(e))
        exit(1) # TODO: do we need to exit here?
    logger.info(text)

def main(event, context):
    
    # Transform dataframes to what we need
    try:
        # 1. Download CSV files and store as S3 objects
        etl_data_functions.downloadFile(url_nyt, 'data-nyt.csv')
        etl_data_functions.downloadFile(url_jh, 'data-jh.csv')
        # 2. Load from S3 into Pandas DataFrames
        df_nyt = etl_data_functions.loadDataFrame('c19data/data-nyt.csv')
        df_jh = etl_data_functions.loadDataFrame('c19data/data-jh.csv')
        # 3. Use DataFrames to get the data we need
        df_transformed = etl_data_functions.transformData(df_nyt, df_jh, country_name)
        # 4. Write transformed DataFrame to S3 for later use
        etl_data_functions.persistDataFrame(df_transformed,'data-final.csv')
        # Connect to PostgreSQL DB
        db_functions.checkDB()
        # Calculate records to write from dataframe 
        rowRecordsWritten = etl_data_functions.determineAndWriteRecords(df_transformed)
        notifyViaSNS(f"Job ran successfully, Updated {format(rowRecordsWritten)} records in the database")
    except Exception as e:
        print(e)
        logger.error("Job failed with error:: {}".format(e))
        notifyViaSNS(f"Job failed with error: {e}")