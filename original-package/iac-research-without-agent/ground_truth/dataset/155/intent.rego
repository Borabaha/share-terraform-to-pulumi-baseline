package main

import rego.v1

default allow := false

# Check if AWS Lambda function is being created
aws_lambda_function_created(resources) if {
	some resource in resources
	resource.type == "aws_lambda_function"
}

# Check if CloudWatch Event Rule is set to invoke Lambda every 15 minutes
cloudwatch_event_rule_for_lambda_valid(resources) if {
	some resource in resources
	resource.type == "aws_cloudwatch_event_rule"
	resource.change.after.schedule_expression == "rate(15 minutes)"
}

# Aggregate all checks
allow if {
	aws_lambda_function_created(input.resource_changes)
	cloudwatch_event_rule_for_lambda_valid(input.resource_changes)
}
