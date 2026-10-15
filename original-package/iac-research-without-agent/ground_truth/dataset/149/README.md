# Prompt 149

## Resources

aws_iam_role, aws_lambda_function, archive_file, aws_iam_policy_document

## Prompt

Create an AWS Lambda function with an IAM role, an IAM policy document for assuming the role, and an archive file for the Lambda function code. The Lambda function should be triggered by a nodejs18 runtime, have a specific handler, and use a "lambda.js" as the source file for the code.

## Difficulty

3

## Intent

Needs to have a defined IAM role. Data for a .zip file, with source file = lambda.js, function name can be anything. For the aws_lambda_function use the defined zip, function name, set handler to anything, and runtime to "nodejs.18x"

