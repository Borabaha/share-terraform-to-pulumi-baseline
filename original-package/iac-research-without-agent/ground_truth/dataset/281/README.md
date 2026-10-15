# Prompt 281

## Resources

aws_kms_key, aws_s3_bucket, aws_s3_bucket_server_side_encryption_configuration

## Prompt

Create an AWS S3 bucket and apply KMS server side encryption that uses a defined KMS key resource.

## Difficulty

2

## Intent

Has one resource "aws_s3_bucket"

Has one resource "aws_kms_key"

Has one resource "aws_s3_bucket_server_side_encryption"
with bucket = bucket id OR name
with rule
    with apply_server_side_encryption_by_default
        with kms_master_key_id = kms key id
        and sse_algorithm = "aws:kms"

