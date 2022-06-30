# Event-Driven ETL Pipeline using Python on AWS

The purpose of this project was to create a Lambda function (triggered from a daily EventBridge rule) that loads and extracts data from multiple sources on the Internet.

This data is then transformed (clean, filter and join) and the transformed data is then stored is a RDS Postgres database. When the job is complete, details of the job are sent to users via a SNS topic.

An AWS Quicksight dashboard was created to visually represent the data stored in the RDS Postgres database.

The Lambda function was written in Python 3 and the AWS SAM framework was used to deploy the Lambda function. 
Terrafrom was used to create the infrastructure stack.
