# Prompt 106

## Resources

aws_s3_bucket, aws_s3_bucket_acl, aws_s3_bucket_public_access_block, aws_s3_bucket_server_side_encryption_configuration

## Prompt

Create an AWS S3 bucket named 'test-bucket' with preventive destruction measures, private ACLs, AES256 server-side encryption, and a public access block restricting public access.

## Difficulty

4

## Intent

has one "aws_s3_bucket" resource
    with one "bucket"

has one "aws_s3_bucket_acl"
    with one "bucket"
    with one "acl" or "access_control_policy"

has one "aws_s3_bucket_public_access_block"
    with one "bucket"

has one "aws_s3_bucket_server_side_encryption_configuration"
    with one "bucket"
    with one "rule"

