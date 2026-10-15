# Prompt 313

## Resources

aws_cloudwatch_event_rule, aws_cloudwatch_event_target, aws_iam_role, aws_iam_role_policy_attachment, aws_lambda_function, aws_lambda_permission, archive_file, aws_iam_policy_document

## Prompt

An AWS EventBridge event rule named "cron" that is scheduled to make target happen everyday at 7 UTC. The target should be linked to a Lambda function with deployment packet at "./supplement/lambda_func.zip".

## Difficulty

5

## Intent

have one "aws_cloudwatch_event_rule" resource
    with "schedule_expression" argument with value "cron(0 7 ** ? *)"
have one "aws_cloudwatch_event_target" resource
    with "rule" argument
    with "arn" argument
have one "aws_lambda_function" resource
    with "function_name" argument with value "cron-lambda-function"
    with "filename" argument with value "cron.zip"
    with "handler" argument with value "cron.lambda_handler"
    with "runtime" argument with value "python3.12"
have one "aws_lambda_permission" resource
    with "function_name" argument with value aws_lambda_function.cron.function_name
    with "action" argument with value "lambda:InvokeFunction"
    with "principal" argument with value "events.amazonaws.com"
    with "source_arn" argument with value aws_cloudwatch_event_rule.cron.arn

