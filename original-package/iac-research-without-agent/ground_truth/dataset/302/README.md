# Prompt 302

## Resources

aws_api_gateway_method, aws_api_gateway_method, aws_api_gateway_resource, aws_api_gateway_rest_api, aws_s3_bucket

## Prompt

An AWS service that holds a web server which allows you to upload cat pictures and provides random cat pictures on demand. Accomplishes this with API Gateway and S3.

## Difficulty

6

## Intent

have one "aws_api_gateway_rest_api" resource
    with "name" argument
have one "aws_api_gateway_resource" resource
    with "rest_api_id" argument linking to aws_api_gateway_rest_api resource id
    with "parent_id" argument linking to aws_api_gateway_rest_api resource root_resource_id
    with "path_part" argument
have two "aws_api_gateway_method" resources
    with "rest_api_id" argument linking to aws_api_gateway_rest_api resource
    with "resource_id" argument linking to aws_api_gateway_resource
    with "http_method" argument with values "GET" and "PUT"
    with "authorization" argument
have one "aws_s3_bucket" resource

