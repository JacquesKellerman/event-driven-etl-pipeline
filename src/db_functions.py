import boto3
import os
import psycopg2

# Initialize boto3 client for Parameter Store
ssm_client = boto3.client('ssm')

# Variables
db_table = os.environ['DB_TABLE']

# Get DB configuration from Parameter store
dbUser = ssm_client.get_parameter(Name='/Covid19DataETL/database/user')
dbPassword = ssm_client.get_parameter(Name='/Covid19DataETL/database/password', WithDecryption=True)
dbEndpoint = ssm_client.get_parameter(Name='/Covid19DataETL/database/endpoint')
dbName = ssm_client.get_parameter(Name='/Covid19DataETL/database/name')

def connectToDB():
    dbConnection = psycopg2.connect(database=dbName['Parameter']['Value'], user=dbUser['Parameter']['Value'],
                                    password=dbPassword['Parameter']['Value'], host=dbEndpoint['Parameter']['Value'],
                                    port=5432)
    return dbConnection

# Check to see if table exists in DB. If not, create table
def checkDB():
    dbConnection = connectToDB()
    dbCursor = dbConnection.cursor()
    try:
        dbCursor.execute(f"CREATE TABLE IF NOT EXISTS {db_table} (report_date TIMESTAMP PRIMARY KEY, cases NUMERIC, deaths NUMERIC, recovered NUMERIC);")
    except Exception as e:
        print(e)
    
    dbConnection.commit()
    dbCursor.close()
    dbConnection.close()

# Calculate data delta to determine what records to insert into DB table
def getLastRecord():
    dbConnection = connectToDB()
    dbCursor = dbConnection.cursor()
    dbCursor.execute(f"SELECT * FROM {db_table} ORDER BY report_date DESC LIMIT 1;")
    lastRecord = dbCursor.fetchall()
    dbCursor.close()
    dbConnection.close()
    return lastRecord[0][0]

# Write records to table
def writeRecords(df_to_write):
    try:
        dbConnection = connectToDB()
        dbCursor = dbConnection.cursor()
        sql_command = "INSERT INTO covid19_data (report_date, cases, deaths, recovered) VALUES (%(report_date)s, %(cases)s, %(deaths)s, %(recovered)s)"
        sql_data = {
            'report_date': df_to_write['Date'],
            'cases': df_to_write['cases'], 
            'deaths': df_to_write['deaths'], 
            'recovered': df_to_write['Recovered']
        }
        dbCursor.execute(sql_command, sql_data)
    except Exception as e:
        print(e)
        exit()
    
    dbConnection.commit()
    dbCursor.close()
    dbConnection.close()