# Prompt 274

## Resources

aws_s3_bucket, aws_s3_bucket, aws_s3_bucket_inventory

## Prompt

Create an AWS S3 bucket and configure a CSV inventory report every week of all current object versions in the bucket and store it in another created bucket. 

## Difficulty

3

## Intent

Has two resources "aws_s3_bucket"

Has one resource "aws_s3_bucket_inventory"
with bucket = first bucket id OR name
with schedule with frequency = "Weekly"
with included_object_versions = "Current"
with destination with bucket with format = "CSV" and bucket_arn = other bucket arn



