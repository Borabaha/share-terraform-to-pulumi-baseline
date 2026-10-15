# Prompt 120

## Resources

aws_s3_bucket, aws_s3_bucket_acl, aws_s3_bucket_ownership_controls

## Prompt

Generate a Terraform configuration for managing AWS S3 resources. Start by creating an S3 bucket with a specific name. Follow this with a configuration block for S3 bucket ownership controls, referencing the bucket's ID and setting the object ownership policy to a predefined setting. Then, define an S3 bucket ACL resource that depends on the successful application of the ownership controls. This ACL should set the bucket access to private and also reference the bucket's ID. Ensure each resource block is defined clearly and connected appropriately through references.

## Difficulty

2

## Intent

Resource "aws_s3_bucket"
has one "bucket"

Resource "aws_s3_bucket_ownership_controls"
has one "bucket"
within "rule", it specifies:
"object_ownership"

Resource "aws_s3_bucket_acl"
has a dependency on "aws_s3_bucket_ownership_controls.example"
has one "bucket"
has one "acl"


