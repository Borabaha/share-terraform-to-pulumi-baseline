# Prompt 0

## Resources

aws_cloudwatch_log_group, aws_cloudwatch_log_resource_policy, aws_route53_query_log, aws_route53_zone, aws_iam_policy_document

## Prompt

Configure a query log that can create a log stream and put log events using Route 53 resources. Name the zone "primary", the cloudwatch log group "aws_route53_example_com", and the cloudwatch log resource policy "route53-query-logging-policy"

## Difficulty

5

## Intent

Has one "aws_route53_zone" resource
    with "name"

Has one "aws_cloudwatch_log_group" resource

Has one "aws_cloudwatch_log_resource_policy" resource
    with "policy_document" enabling "logs:CreateLogStream" and "logs:PutLogEvents"
    with "policy_name"

Has one "aws_route53_query_log" resource
    with "cloudwatch_log_group_arn" referencing the "aws_cloudwatch_log_group" resource
    with "zone_id" referencing the "aws_route53_zone" resource
    and depends on the "aws_cloudwatch_log_resource_policy" resource

