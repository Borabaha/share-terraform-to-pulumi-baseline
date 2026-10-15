# Prompt 123

## Resources

aws_s3_bucket, aws_s3_bucket_ownership_controls

## Prompt

Generate a Terraform configuration for creating an AWS S3 bucket and setting its ownership controls. Define a resource for an S3 bucket with a specified name. Follow this by configuring ownership controls for this bucket, referencing its ID. Within the ownership controls, set a rule to specify the object ownership as 'BucketOwnerPreferred'. Ensure that the resources are properly linked using references, and the configuration is clearly laid out to reflect these settings.

## Difficulty

2

## Intent

Resource "aws_s3_bucket" 
has one "bucket"

Resource "aws_s3_bucket_ownership_controls"
has one "bucket"
within the "rule", it specifies:
"object_ownership"

