package main

import rego.v1

default allow := false

# Check for DynamoDB table creation
dynamodb_table_created(resources) if {
	some resource in resources
	resource.type == "aws_dynamodb_table"
	resource.change.actions[_] == "create"
}

# Aggregate checks for DynamoDB table
allow if {
	dynamodb_table_created(input.resource_changes)
}
