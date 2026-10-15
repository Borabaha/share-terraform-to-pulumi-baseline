# Prompt 109

## Resources

aws_s3_bucket, aws_s3_bucket_acl, aws_s3_bucket_lifecycle_configuration, aws_s3_bucket_versioning

## Prompt

Create an AWS S3 bucket named 'wellcomecollection-platform-infra' with preventive destruction measures. Set the bucket ACL to 'private' and configure a lifecycle policy for automatic deletion of objects with a 'tmp/' prefix after 30 days. Implement versioning and set up lifecycle rules to transition old versions to the 'STANDARD_IA' storage class after 30 days and delete noncurrent versions after 90 days.

## Difficulty

4

## Intent

has one aws_s3_bucket resource
with bucket

has one aws_s3_bucket_acl resource
with bucket 
with acl

has one aws_s3_bucket_lifecycle_configuration resource
with bucket
with rule
     with id
     with status
     with action
     with transition
          with days
          with storage_class
with expiration
     with days

has one aws_s3_bucket_versioning resource
with bucket
with versioning_configuration
     with status (can be "Enabled" or "Suspended")

