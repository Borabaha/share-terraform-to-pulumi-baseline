# Prompt 311

## Resources

aws_cloudwatch_event_rule, aws_cloudwatch_event_target, aws_iam_role, aws_iam_role_policy_attachment, aws_lambda_function, aws_lambda_permission, aws_iam_policy_document

## Prompt

An AWS service that runs a code everyday at 7 UTC. Accomplish this using the following services: AWS EventBridge, AWS Lambda. Add any necessary services.

## Difficulty

5

## Intent

have one "aws_cloudwatch_event_rule" resource
    with "schedule_expression" argument with value "cron(0 7 * * ? *)"
have one "aws_cloudwatch_event_target" resource
    with "rule" argument
    with "arn" argument
have one "aws_lambda_function" resource
    with "function_name" argument
    with "role" argument
    with "filename" argument
    with "handler" argument
    with "runtime" argument
have one "aws_lambda_permission" resource
    with "function_name" argument with value aws_lambda_function.cron.function_name
    with "action" argument with value "lambda:InvokeFunction"
    with "principal" argument with value "events.amazonaws.com"
    with "source_arn" argument with value aws_cloudwatch_event_rule.cron.arn

