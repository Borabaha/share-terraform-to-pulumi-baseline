# Prompt 185

## Resources

aws_iam_role, aws_lambda_function, archive_file, aws_iam_policy_document

## Prompt

Create an AWS Lambda function. The function should be triggered by a nodejs18 runtime,use a "lambda.js" as the source code and a "index.js" as the handler. Please declare all necessary resources.

## Difficulty

3

## Intent

Needs to have a defined IAM role. Data for a .zip file, with source file = lambda.js, function name can be anything. For the aws_lambda_function use the defined zip, function name, set handler to anything, and runtime to "nodejs.18x"

