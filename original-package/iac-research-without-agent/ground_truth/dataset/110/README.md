# Prompt 110

## Resources

aws_s3_bucket, aws_s3_bucket_logging

## Prompt

Create a bucket "a". Then configure logging for the bucket to send access logs to another bucket named 'logging-680235478471' with a prefix of 'log/' in the target bucket.

## Difficulty

2

## Intent

has one aws_s3_bucket resource
with bucket

has one aws_s3_bucket_logging resource
with bucket
with target_bucket
with target_prefix

