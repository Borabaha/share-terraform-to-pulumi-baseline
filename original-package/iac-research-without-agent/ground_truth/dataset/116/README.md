# Prompt 116

## Resources

aws_s3_bucket, aws_s3_bucket_acl, aws_s3_bucket_policy

## Prompt

Create a Terraform configuration that defines an AWS S3 bucket, an ACL for the bucket, and a bucket policy allowing s3:GetObject actions with a condition based on the AWS Referer header. The bucket should have a unique name like "my_unique_bucket_name," and the policy should grant access to all principals. 

## Difficulty

3

## Intent

Resource "aws_s3_bucket"
has one "bucket"

Resource "aws_s3_bucket_acl"
has one "bucket"
has one "acl"

Resource "aws_s3_bucket_policy"
has one "bucket"
has one "policy"

