# Prompt 112

## Resources

aws_s3_bucket, aws_s3_bucket_object_lock_configuration

## Prompt

Create an AWS S3 bucket named 'example-bucket' with object lock enabled. Configure object lock compliance mode with a retention period of 30 days for objects in the bucket.

## Difficulty

2

## Intent

has one aws_s3_bucket resource
with bucket

has one aws_s3_bucket_object_lock_configuration resource
with bucket
with rule
     with default_retention
          with mode (GOVERNANCE or COMPLIANCE)
          with days or years

