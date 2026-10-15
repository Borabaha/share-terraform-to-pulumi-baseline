package main

import rego.v1

default allow := false

# Check if the AWS DynamoDB table is being created in us-east-1
aws_dynamodb_table_valid(resources) if {
	some resource in resources
	resource.type == "aws_dynamodb_table"
	resource.change.after.billing_mode == "PAY_PER_REQUEST"
}

# Aggregate all checks
allow if {
	aws_dynamodb_table_valid(input.resource_changes)
}
