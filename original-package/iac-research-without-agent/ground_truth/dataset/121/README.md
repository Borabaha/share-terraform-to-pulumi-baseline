# Prompt 121

## Resources

aws_s3_bucket, aws_s3_bucket, aws_s3_bucket_acl, aws_s3_bucket_acl, aws_s3_bucket_logging

## Prompt

Create a Terraform configuration for setting up AWS S3 buckets with specific access control and logging features. Start by defining two S3 buckets with distinct names. Next, establish access control for each bucket with predefined ACL settings, ensuring one is set to private and the other to allow log delivery writes. Finally, configure S3 bucket logging for one of the buckets to send its logs to the other, specifying a log file prefix. Ensure all resources are appropriately linked using their identifiers and that the configuration reflects the correct dependencies and settings as described.

## Difficulty

3

## Intent

Resource "aws_s3_bucket"
has one "bucket"

Resource "aws_s3_bucket_acl" 
has one "bucket"
has one "acl" set to "private"

Resource "aws_s3_bucket"
has one "bucket"

Resource "aws_s3_bucket_acl"
has one "bucket"
has one "acl" set to "log-delivery-write"

Resource "aws_s3_bucket_logging"
has one "bucket"
has one "target_bucket"
has one "target_prefix"

