# Prompt 114

## Resources

aws_s3_bucket, aws_s3_bucket_public_access_block

## Prompt

Implement public access block settings for an AWS S3 bucket named 'pike-680235478471' to block public ACLs, public policies, and restrict public buckets.

## Difficulty

2

## Intent

has one aws_s3_bucket resource
with bucket

has one aws_s3_bucket_public_access_block resource
with bucket
with block_public_acls (boolean)
with block_public_policy (boolean)
with ignore_public_acls (boolean)
with restrict_public_buckets (boolean)

