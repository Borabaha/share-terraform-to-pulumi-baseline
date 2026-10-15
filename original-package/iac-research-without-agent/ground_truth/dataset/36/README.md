# Prompt 36

## Resources

aws_codebuild_project, aws_iam_role, aws_s3_bucket

## Prompt

create a AWS codebuild project resource with example iam role, an example GITHUB source, artifact, and a cache

## Difficulty

5

## Intent

Has one "aws_iam_role" resource, one "aws_s3_bucket" resource, and one "aws_codebuild_project" resource with a "cache" block, the "type" argument within the "artifacts" block not equal to "NO_ARTIFACTS", and the "type" argument within the "source" block equal to "GITHUB"

