package job_scheduler

import rego.v1

default valid := false
default rule_valid := false
default lambda_valid := false
default target_valid := false
default lambda_permission_valid := false


# Validate Lambda permission
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

# Validate event target
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

# Validate Lambda function
lambda_valid if {
    some lambda in input.configuration.root_module.resources
    lambda.type == "aws_lambda_function"

    some role in input.configuration.root_module.resources
    role.type == "aws_iam_role"

    role.address in lambda.expressions.role.references
    lambda.expressions.function_name
    #lambda.expressions.filename.constant_value == "./supplement/lambda_func.py"
    lambda.expressions.handler
    lambda.expressions.runtime
}

# Validate CloudWatch Event Rule
rule_valid if {
    some rule in input.configuration.root_module.resources
    rule.type == "aws_cloudwatch_event_rule"

    some role in input.configuration.root_module.resources
    role.type == "aws_iam_role"

    rule.expressions.schedule_expression.constant_value == "cron(0 7 * * ? *)"
}

# Final validation condition
valid if {
    rule_valid
    lambda_valid
    target_valid
    lambda_permission_valid
}
