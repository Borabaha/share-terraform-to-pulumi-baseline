# Prompt 276

## Resources

aws_s3_bucket, aws_s3_bucket_notification, aws_sns_topic

## Prompt

Create an AWS S3 bucket and send a SNS notification whenever a .log object is created in the bucket. Do not include policies required for this. 

## Difficulty

2

## Intent

Has one resource "aws_s3_bucket"

Has one resource "aws_sns_topic"

Has one resource "aws_s3_bucket_notification"
with bucket = bucket id OR name
with topic
    with topic arn = sns topic arn 
    and events = ["s3:ObjectCreated:*"]
    and filter_suffix = ".log"

