# Prompt 119

## Resources

aws_kms_key, aws_s3_bucket, aws_s3_bucket_server_side_encryption_configuration

## Prompt

Create a Terraform configuration for an AWS environment. Start by defining a KMS key with a specific description and a set deletion window in days. Next, define an S3 bucket with a specified name. Finally, configure server-side encryption for the S3 bucket using the previously defined KMS key. The encryption should use the KMS algorithm specified in AWS. Include resource blocks for each component and ensure the bucket encryption references the KMS key's ARN and uses the KMS algorithm for encryption.

## Difficulty

2

## Intent

Resource "aws_kms_key"
has one "description"
has one "deletion_window_in_days"

Resource "aws_s3_bucket"
has one "bucket"

Resource "aws_s3_bucket_server_side_encryption_configuration"
has one "bucket"
within "rule", it specifies:
"kms_master_key_id"
"sse_algorithm"

