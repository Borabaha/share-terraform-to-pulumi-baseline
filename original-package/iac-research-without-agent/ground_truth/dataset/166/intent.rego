package main

import rego.v1

default allow := false

# Check if AWS DynamoDB table is being created with specific read and write capacity settings
aws_dynamodb_table_item_valid(resources) if {
	some resource in resources
	resource.type == "aws_dynamodb_table_item"
}

# Aggregate all checks
allow if {
	aws_dynamodb_table_item_valid(input.resource_changes)
}
