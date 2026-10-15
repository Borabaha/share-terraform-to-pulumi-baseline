# Prompt 298

## Resources

aws_codebuild_project, aws_iam_policy, aws_iam_role, aws_iam_role_policy_attachment, aws_s3_bucket, aws_security_group, aws_subnet, aws_vpc, aws_iam_policy_document, aws_iam_policy_document

## Prompt

Infrastructure for an autograder for a CS class. The autograde needs to run students' code stored on GitHub in a specific environment and store the result. Make sure that the autograder prevents the students' code from reaching the internet. Accomplish this using AWS CodeBuild and AWS VPC.

## Difficulty

6

## Intent

have one "aws_codebuild_project" resource
  with "artifacts" argument block
    with "type" argument with value "S3"
    with "location" argument
    with "name" argument
  with "environment" argument block
    with "computer_type" argument
    with "image" argument
    with "type" argument
  with "source" argument block
    with "type" argument with value "GITHUB"
    with "location" argument
  with "vpc_config" argument block
    with "vpc_id" argument
    with "subnets" argument
    with "security_group_ids" argument
have one "aws_vpc" resource
  with "cidr_block" argument
have one "aws_subnet" argument
  with "vpc_id" argument
  with "cidr_block" argument
with one "aws_security_group" resource
  with "vpc_id" argument

