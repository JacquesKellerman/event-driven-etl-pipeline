import pandas as pd
import boto3
import io
import requests
import os

from db_functions import getLastRecord, writeRecords

s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')

# Download CSV data file and save it as an S3 object
def downloadFile(url, file_name):
    try:
        body = requests.get(url).content.strip(b'\n')
        s3_path = "c19data/" + file_name
        s3_resource.Bucket(os.environ['S3_BUCKET']).put_object(Key = s3_path, Body = body)
    except Exception as e:
        print(e)
        exit(1)

# Creates dataframe from S3 object
def loadDataFrame(key):
    obj = s3_client.get_object(Bucket = os.environ['S3_BUCKET'], Key = key)
    csv_file = obj['Body'].read().strip(b'\n')
    data_frame = pd.read_csv(io.BytesIO(csv_file), low_memory = False)
    return data_frame

# Save transformed dataframe as S3 object
def persistDataFrame(df_final, file_name):
    try:
        s3_path = "c19data/" + file_name
        df_final_csv = io.StringIO()
        df_final.to_csv(df_final_csv)
        s3_resource.Bucket(os.environ['S3_BUCKET']).put_object(Key = s3_path, Body = df_final_csv.getvalue())
    except Exception as e:
        print(e)
        exit(1)

#  Sends the data to the database that only has a date higher than current latest in the db
def cleanDataSet(data_frame, country, columns, col='Country/Region'):
    try:
        data_frame.drop(data_frame[data_frame[col] != country].index, inplace = True)
        data_frame.drop(columns, axis = 1, inplace = True)
        return
    except Exception as e:
        print(e)
        exit(1)

def transformData(df_nyt, df_jh, country_name):
    try:
        # 1. Convert date column in Date object
        df_nyt.rename(columns = {"date":"Date"},inplace = True) 
        df_nyt['Date']= pd.to_datetime(df_nyt['Date'],format='%Y-%m-%d')
        df_nyt.set_index('Date', inplace=True)

        # 2. Convert date column in Date object
        # 3. Convert Recovered column in integer object and replace NA with 0 value
        df_jh = df_jh[df_jh['Country/Region']==country_name].drop(columns='Country/Region')
        
        df_jh.drop(columns=['Province/State','Confirmed','Deaths',],inplace=True)
        
        df_jh['Date']= pd.to_datetime(df_jh['Date'],format='%Y-%m-%d')
        df_jh.set_index('Date', inplace=True)
        df_jh['Recovered'] = df_jh['Recovered'].fillna(0).astype('int64')

        # 4. Remove data not needed from John Hopkins dataframe
        #cleanDataSet(df_jh, country_name, ['Deaths', 'Country/Region', 'Province/State', 'Confirmed'])
        
        # 5. Merge two datasets on common date values
        df_mrgd = df_nyt.join(df_jh, how='inner')
        df_mrgd.reset_index(inplace=True)

        print("Merged DataFrame - No. of rows: " + str(len(df_mrgd.index)))
        print("Merged DataFrame - No. of columns: " + str(len(df_mrgd.columns)))
        
        return df_mrgd
    except Exception as e:
        print(e)
        exit(1)

def determineAndWriteRecords(data_set):
    try:
        latestRecord = pd.to_datetime(getLastRecord(), format='%Y-%m-%d')
        print("Last record date: " + str(latestRecord))
        dataToWrite = data_set[data_set['Date'] > latestRecord]
        print("DataFrame to write - No. of rows: " + str(len(dataToWrite.index)))
        print("DataFrame to write - No. of columns: " + str(len(dataToWrite.columns)))
        if len(dataToWrite) > 0:
            dataToWrite.apply(lambda x: writeRecords(x), axis = 1)
        print("Data rows written: " + str(len(dataToWrite)))
        return len(dataToWrite)
    except Exception as e:
        print(e)