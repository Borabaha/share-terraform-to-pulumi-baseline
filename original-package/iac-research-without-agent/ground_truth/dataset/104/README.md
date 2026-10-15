# Prompt 104

## Resources

aws_s3_bucket, aws_s3_bucket_policy

## Prompt

Create an AWS S3 bucket named 'my_bucket' and define an S3 bucket policy to deny access from a specific IP address. Ensure that the S3 bucket policy includes a version number, an identifier, and a statement that denies all S3 actions for the specified IP address. Use the 'jsonencode' function to encode the policy in JSON format.

## Difficulty

3

## Intent

has one "aws_s3_bucket" resource
    with one "bucket"

has one "aws_s3_bucket_policy"
     with one "bucket"
     with one "policy"

