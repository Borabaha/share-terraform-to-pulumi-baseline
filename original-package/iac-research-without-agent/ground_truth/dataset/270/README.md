# Prompt 270

## Resources

aws_s3_bucket, aws_s3_bucket_acl, aws_s3_bucket_ownership_controls

## Prompt

Create S3 bucket with bucket name = "mybucket" and set the ownership control of the S3 bucket to be bucket owner preferred.
Then create an ACL resource that depends on ownership control and makes bucket private. Use bucket references, NOT the name of the bucket.

## Difficulty

2

## Intent

Has an aws_s3_bucket resource

Has an aws_s3_bucket_ownership_controls
with bucket = bucket id
and rule with object_ownership = "BucketOwnerPreferred"

Has an aws_s3_bucket_acl

