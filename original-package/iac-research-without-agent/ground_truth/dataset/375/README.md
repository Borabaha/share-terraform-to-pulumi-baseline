# Prompt 375

## Resources

aws_lightsail_bucket, aws_lightsail_bucket_resource_access, aws_lightsail_instance

## Prompt

Create a lightsail resource access to a bucket.

## Difficulty

3

## Intent

have one aws_lightsail_bucket
    with name
    with bundle_id

have one aws_lightsail_bucket_resource_access
    with bucket_name
    with resource_name

have one "aws_lightsail_instance" resource
    with "name" argument
    with "availability_zone" argument
    with "blueprint_id" argument
    with "bundle_id" argument

