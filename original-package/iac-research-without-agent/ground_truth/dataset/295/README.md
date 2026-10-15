# Prompt 295

## Resources

aws_codebuild_project, aws_iam_policy, aws_iam_role, aws_iam_role_policy_attachment, aws_s3_bucket, aws_iam_policy_document, aws_iam_policy_document

## Prompt

Infrastructure for an autograder for a CS class. The autograder needs to run students' code stored on GitHub in a specific environment and store the result. Accomplish this using the following services: AWS S3, AWS CodeBuild. Add any necessary services.

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
    with "computer_type" argument
    with "image" argument
    with "type" argument
  with "source" argument block
    with "type" argument with value "GITHUB"
    with "location" argument

