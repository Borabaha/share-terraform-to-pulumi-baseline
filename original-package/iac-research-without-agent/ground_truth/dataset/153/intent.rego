package main

import rego.v1

default allow := false

aws_dynamodb_table_valid(resources) if {
	some resource in resources
	resource.type == "aws_dynamodb_table"
}

aws_lambda_function_valid(resources) if {
	some resource in resources
	resource.type == "aws_lambda_function"
}

# Check for Lambda event source mapping from DynamoDB
aws_lambda_event_source_mapping_valid(resources) if {
	some resource in resources
	resource.type == "aws_lambda_event_source_mapping"
}

# Aggregate all checks
allow if {
	aws_dynamodb_table_valid(input.resource_changes)
	aws_lambda_function_valid(input.resource_changes)
	aws_lambda_event_source_mapping_valid(input.resource_changes)
}
