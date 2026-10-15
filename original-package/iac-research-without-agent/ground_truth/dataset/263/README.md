# Prompt 263

## Resources

aws_iam_user, aws_iam_user_ssh_key

## Prompt

Create a basic AWS IAM user with a basic SSH key attached.

## Difficulty

2

## Intent

Has one "aws_iam_user" resource
with one "name" with any value

Has one "aws_iam_user_ssh_key" resource
with one "username" with value "aws_iam_user.{USER NAME}.name"
with one "encoding" with value "SSH"
with one "public_key" with any value

