# Prompt 297

## Resources

aws_codebuild_project, aws_iam_policy, aws_iam_role, aws_iam_role_policy_attachment, aws_s3_bucket, aws_iam_policy_document, aws_iam_policy_document

## Prompt

An AWS S3 bucket to store code build output. An AWS CodeBuild project resource with an artifacts argument block of type S3 to store students' code build output with location being the S3 bucket resource, an environment argument block with "BUILD_GENERAL1_SMALL" computer_type, "alpine" image, and "LINUX_CONTAINER" type, and a source argument block of "GITHUB" type, 1 git_clone_depth, and "github.com/source-location" location.

## Difficulty

4

## Intent

have one "aws_s3_bucket" resource
have one "aws_codebuild_project" resource
  with "artifacts" argument block
    with "type" argument with value "S3"
    with "location" argument
    with "name" argument
  with "environment" argument block
    with "computer_type" argument with value "BUILD_GENERAL1_SMALL"
    with "image" argument with value "alpine"
    with "type" argument with value "LINUX_CONTAINER"
  with "source" argument block
    with "type" argument with value "GITHUB"
    with "location" argument with value "github.com/source-location"

