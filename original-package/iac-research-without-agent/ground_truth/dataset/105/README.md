# Prompt 105

## Resources

aws_s3_bucket, aws_s3_bucket_metric, aws_s3_bucket_object

## Prompt

Set up an AWS S3 bucket named 'my_bucket' with forced destruction enabled for cleanup purposes. Create an S3 bucket metric named 'my_bucket_metric' to monitor the entire bucket's activity. Additionally, include an S3 bucket object named 'my_object' with a specific key and content to be stored in the bucket.

## Difficulty

2

## Intent

has one "aws_s3_bucket" resource
    with one "bucket"

has one "aws_s3_bucket_metric"
    with one "bucket"
    with one "name

has one "aws_s3_bucket_object"
    with one "bucket"
    with one "key"


