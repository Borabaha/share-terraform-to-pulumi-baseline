# Prompt 118

## Resources

aws_s3_bucket, aws_s3_bucket_object_lock_configuration, aws_s3_bucket_versioning

## Prompt

Create a Terraform configuration that sets up an AWS S3 bucket named "mybucket" with versioning enabled. Additionally, configure object lock retention for compliance mode with a retention period of 5 days. Ensure that the object lock configuration is applied to the same bucket as versioning. Use appropriate resource types and dynamic references for bucket IDs and ARNs in the configuration.

## Difficulty

3

## Intent

Resource "aws_s3_bucket"
has one "bucket"

Resource "aws_s3_bucket_versioning"
has one "bucket"
with one "status" in "versioning_configuration"

Resource "aws_s3_bucket_object_lock_configuration"
has one "bucket"
with one "mode" and "days" in "default_retention" within "rule"

