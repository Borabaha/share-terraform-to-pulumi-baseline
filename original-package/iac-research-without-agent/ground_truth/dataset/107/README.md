# Prompt 107

## Resources

aws_s3_bucket, aws_s3_bucket_versioning

## Prompt

Create a bucket "sample". Implement versioning resource for the AWS S3 bucket named 'sample' with the versioning status set to 'Enabled' and specify the expected_bucket_owner as '123456789012' to ensure ownership consistency.

## Difficulty

2

## Intent

has one aws_s3_bucket resource
with bucket

has one "aws_s3_bucket_versioning" resource
     with bucket
     with versionaning_configuration
          with status

