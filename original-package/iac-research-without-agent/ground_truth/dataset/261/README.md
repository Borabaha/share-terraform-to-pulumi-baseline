# Prompt 261

## Resources

aws_iam_group, aws_iam_group_membership, aws_iam_user, aws_iam_user

## Prompt

Create two basic AWS IAM users that are a part of a basic IAM group

## Difficulty

3

## Intent

Has one "aws_iam_group" resource
with one "name" with any value

Has one "aws_iam_user" resource
with one "name" with any value

Has another "aws_iam_user" resource
with one "name" with any value

Has one "aws_iam_group_membership" resource
with one "name" with any value
with one "users" with the two user resource names
with one "group" with the group resource name

