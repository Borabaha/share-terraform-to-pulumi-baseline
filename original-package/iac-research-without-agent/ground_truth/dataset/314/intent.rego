package job_scheduler

import rego.v1

default valid := false
default rule_valid := false
default lambda_valid := false
default target_valid := false
default lambda_permission_valid := false


# Lambda Permission Validation
lambda_permission_valid if {
    some lambda_permission in input.configuration.root_module.resources
    lambda_permission.type == "aws_lambda_permission"

    some lambda in input.configuration.root_module.resources
    lambda.type == "aws_lambda_function"

    some rule in input.configuration.root_module.resources
    rule.type == "aws_cloudwatch_event_rule"

    lambda_permission.expressions.action.constant_value == "lambda:InvokeFunction"
    lambda_permission.expressions.principal.constant_value == "events.amazonaws.com"
    lambda.address in lambda_permission.expressions.function_name.references
    rule.address in lambda_permission.expressions.source_arn.references
}

# Event Target Validation
target_valid if {
    some target in input.configuration.root_module.resources
    target.type == "aws_cloudwatch_event_target"

    some lambda in input.configuration.root_module.resources
    lambda.type == "aws_lambda_function"

    some rule in input.configuration.root_module.resources
    rule.type == "aws_cloudwatch_event_rule"

    lambda.address in target.expressions.arn.references
    rule.address in target.expressions.rule.references
}

# Lambda Function Validation
lambda_valid if {
    some lambda in input.configuration.root_module.resources
    lambda.type == "aws_lambda_function"

    some role in input.configuration.root_module.resources
    role.type == "aws_iam_role"

    role.address in lambda.expressions.role.references
    lambda.expressions.function_name.constant_value == "cron-lambda-function"
    #lambda.expressions.filename.constant_value == "cron.zip"
    #lambda.expressions.handler.constant_value == "cron.lambda_handler"
    lambda.expressions.runtime.constant_value == "python3.12"
}

# CloudWatch Event Rule Validation
rule_valid if {
    some rule in input.configuration.root_module.resources
    rule.type == "aws_cloudwatch_event_rule"

    some role in input.configuration.root_module.resources
    role.type == "aws_iam_role"

    rule.expressions.schedule_expression.constant_value == "cron(0 7 * * ? *)"
}

# Final Validation Condition
valid if {
    rule_valid
    lambda_valid
    target_valid
    lambda_permission_valid
}
