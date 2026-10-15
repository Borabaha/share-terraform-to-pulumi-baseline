# Prompt 292

## Resources

aws_s3_bucket, aws_s3_bucket, aws_s3_bucket_logging

## Prompt

Create a S3 bucket and a second S3 bucket. Then create an example logging resource for the first S3 bucket that stores logs in the second bucket. Make sure the log object keys have a prefix of "log/".

## Difficulty

2

## Intent

Has two aws_s3_bucket

Has an aws_s3_bucket_logging
with bucket = bucket id OR name
with target_bucket = second bucket id OR name
with target_prefix = "log/"

