package main

import rego.v1

default allow := false

# Check for Lambda Function URL Resource
aws_lambda_invocation_valid(resources) if {
	some resource in resources
	resource.type == "aws_lambda_invocation"
}

aws_lambda_function_valid(resources) if {
	some resource in resources
	resource.type == "aws_lambda_function"
}

# Aggregate all checks
allow if {
	aws_lambda_invocation_valid(input.resource_changes)
	aws_lambda_function_valid(input.resource_changes)
}
