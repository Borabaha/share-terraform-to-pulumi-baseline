# Prompt 273

## Resources

aws_s3_bucket, aws_s3_bucket, aws_s3_bucket_inventory

## Prompt

Create S3 bucket with bucket name = "mybucket" and an inventory configuration resource for the bucket that reports daily.

## Difficulty

3

## Intent

Has two resources "aws_s3_bucket"

Has one resource "aws_s3_bucket_inventory"
with bucket = first bucket id OR name
with schedule with frequency = "Daily"

