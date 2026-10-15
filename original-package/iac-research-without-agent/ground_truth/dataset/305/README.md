# Prompt 305

## Resources

aws_api_gateway_integration, aws_api_gateway_integration, aws_api_gateway_method, aws_api_gateway_method, aws_api_gateway_resource, aws_api_gateway_rest_api, aws_dynamodb_table, aws_iam_role, aws_iam_role, aws_lambda_function, aws_lambda_function, aws_lambda_permission, aws_lambda_permission, aws_s3_bucket, archive_file, archive_file

## Prompt

An API Gateway Rest API named "caas" that has a resource endpoint named "caas_cat" with a path_part "cat" linking to two methods "caas_get" and "caas_put" with http_method "GET" and "PUT." Each of the methods should have a corresponding Lambda function that the API Gateway will have permission to access. A S3 bucket that stores cat pictures which will be accessed by a Lambda function, and a DynamoDB table with one keyed attribute, strings "name" of the cat.

## Difficulty

6

## Intent

have one "aws_api_gateway_rest_api" resource
    with "name" argument name
have one "aws_api_gateway_resource" resource
    with "rest_api_id" argument linking to aws_api_gateway_rest_api resource id
    with "parent_id" argument linking to aws_api_gateway_rest_api resource root_resource_id
    with "path_part" argument with value "cat"
have two "aws_api_gateway_method" resources
    with "rest_api_id" argument linking to aws_api_gateway_api resource id
    with "resource_id" linking to aws_api_gateway_resource resource
    with "authorization" argument with value "NONE"
    with "http_method" argument with values "GET" and "PUT"
have one "aws_s3_bucket" resource
have one "aws_dynamodb_table" resource
    with "name" argument
    with "hash_key" argument with value "name"
    with "attribute" argument block
        with "name" argument with value "name"
        with "type" argument with value "S"
with two "aws_lambda_function" resources
    with "function_name" argument
    with "role" argument linking to aws_iam_role resources
    with "environment" argument block
        with "variables" argument block linking to the aws_s3_bucket
with two "aws_lambda_permission" resources
    with "action" argument with value "lambda:InvokeFunction"
    with "principal" argument with value "apigateway.amazonaws.com"
    with "function_name" argument linking to aws_lambda_function resource
    with "source_arn" argument linking to aws_api_gateway_rest_api (two different end points)
with two "aws_api_gateway_integration" resources
    with "rest_api_id" argument linking to aws_api_gateway_rest_api resource
    with "resource_id" argument linking to aws_api_gateway_resource resource
    with "http_method" argument linking to aws_api_gateway_method resource
    with "type" argument with value "AWS_PROXY"
    with "integration_http_method" argument with values "GET" and "PUT"

