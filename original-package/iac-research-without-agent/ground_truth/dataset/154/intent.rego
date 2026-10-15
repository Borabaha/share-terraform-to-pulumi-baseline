package main

import rego.v1

default allow := false

# Check if the AWS Lambda Layer Version is valid
aws_lambda_layer_version_valid(resources) if {
	some resource in resources
	resource.type == "aws_lambda_layer_version"
	resource.change.after.filename == "lambda_layer_payload.zip"
}

# Aggregate all checks
allow if {
	aws_lambda_layer_version_valid(input.resource_changes)
}
