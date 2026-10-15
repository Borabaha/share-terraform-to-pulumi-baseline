# Prompt 115

## Resources

aws_s3_bucket, aws_s3_bucket, aws_s3_bucket_acl, aws_s3_bucket_ownership_controls, aws_s3_bucket_policy, aws_s3_bucket_public_access_block

## Prompt

Create an AWS S3 bucket for CloudGoat data storage, with a dynamic bucket name incorporating the bucket_suffix "test" from a variable. Configure the bucket with private ACLs and ownership controls for ObjectWriter access. Set up another S3 bucket for web data storage with a similar dynamic name. Upload an object 'order_data2.csv' to the web data bucket from a local file path. Implement public access block settings for the web data bucket to ignore public ACLs, block public ACLs, and restrict public buckets. Lastly, create a bucket policy allowing 's3:PutObject' action for all principals on the web data bucket's objects.

## Difficulty

5

## Intent

has one aws_s3_bucket resource
with bucket

has one aws_s3_bucket_acl resource
with bucket
with acl

has one aws_s3_bucket_ownership_controls resource
with bucket
with rule
with object_ownership

has one aws_s3_object resource
with bucket
with key
with source

has one aws_s3_bucket_public_access_block resource
with bucket
with block_public_acls (boolean)
with block_public_policy (boolean)
with ignore_public_acls (boolean)
with restrict_public_buckets (boolean)

has one aws_s3_bucket_policy resource
with bucket
with policy

