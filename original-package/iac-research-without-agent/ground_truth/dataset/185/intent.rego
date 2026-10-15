package main

import rego.v1

default allow := false

# Check for IAM Role for Lambda
aws_iam_role_for_lambda_valid(resources) if {
	some resource in resources
	resource.type == "aws_iam_role"
}

# Check for AWS Lambda Function with specific configurations
aws_lambda_function_valid(resources) if {
	some resource in resources
	resource.type == "aws_lambda_function"
	resource.change.after.runtime == "nodejs18.x"
	resource.change.after.handler
	resource.change.after.filename
}


# Aggregate all checks
allow if {
	aws_iam_role_for_lambda_valid(input.resource_changes)
	aws_lambda_function_valid(input.resource_changes)
}
