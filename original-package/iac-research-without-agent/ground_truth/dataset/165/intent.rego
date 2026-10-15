package main

import rego.v1

default allow := false

# Check if AWS DynamoDB table is being created with specific read and write capacity settings
aws_dynamodb_table_custom_capacity_valid(resources) if {
	some resource in resources
	resource.type == "aws_dynamodb_table"
	resource.change.after.read_capacity == 20
	resource.change.after.write_capacity == 20
}

# Aggregate all checks
allow if {
	aws_dynamodb_table_custom_capacity_valid(input.resource_changes)
}
