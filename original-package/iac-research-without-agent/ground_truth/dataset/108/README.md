# Prompt 108

## Resources

aws_dynamodb_table, aws_s3_bucket, aws_s3_bucket_public_access_block, aws_s3_bucket_server_side_encryption_configuration, aws_s3_bucket_versioning

## Prompt

Set up an AWS S3 bucket and DynamoDB table for Terraform state management. Ensure the S3 bucket has preventive measures against accidental deletion and is configured with versioning enabled, server-side encryption using AES256, and public access restrictions. Create a DynamoDB table with a hash key named 'LockID' using 'PAY_PER_REQUEST' billing mode for Terraform locking.

## Difficulty

5

## Intent

has one aws_s3_bucket_versioning resource
with bucket    
with status

has one aws_dynamodb_table resource
with name
with hash_key

has one aws_s3_bucket_lifecycle_configuration resource
with bucket 
with rule
    with id
    with status
    with action
    with transition
        with days
        with storage_class

has one aws_s3_bucket_server_side_encryption_configuration resource
with bucket
with rule
    with apply_server_side_encryption_by_default
    with sse_algorithm

has one aws_s3_bucket_public_access_block resource
with bucket
with block_public_acls (boolean)
with block_public_policy (boolean)
with ignore_public_acls (boolean)
with restrict_public_buckets(boolean)

has one aws_dynamodb_table resource
with name  
with hash_key  
with attribute
    with name
    with type

