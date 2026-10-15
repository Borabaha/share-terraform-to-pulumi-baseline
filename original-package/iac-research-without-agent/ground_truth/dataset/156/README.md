# Prompt 156

## Resources

aws_cloudwatch_event_rule, aws_cloudwatch_event_target, aws_iam_role, aws_lambda_function, archive_file, aws_iam_policy_document

## Prompt

Trigger a "aws_lambda_function" called test_lambda whenever an EC2 image is created

## Difficulty

4

## Intent

Needs to have an aws_lambda_function defined. Create a aws_cloudwatch_event_rule to trigger on EC2 creation and aws_lambda_permission to have permission to run lambda function. Create a target to trigger the lambda function.

