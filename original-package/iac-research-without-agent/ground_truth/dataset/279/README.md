# Prompt 279

## Resources

aws_s3_bucket, aws_s3_bucket_object_lock_configuration

## Prompt

Create a S3 bucket with bucket name = "mybucket" and object lock enabled. Then, add an object lock configuration resource for the new bucket.

## Difficulty

2

## Intent

Has an aws_s3_bucket resource
with object_lock_enabled = true

Has an aws_s3_object_lock resource
with bucket = bucket id OR name
and a correct rule

