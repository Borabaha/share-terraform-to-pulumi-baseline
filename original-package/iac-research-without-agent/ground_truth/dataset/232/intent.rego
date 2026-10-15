package main

import rego.v1

default allow := false

# Check for DynamoDB table creation or update
dynamodb_table_modified(resources) if {
	some resource in resources
	resource.type == "aws_dynamodb_table"
	resource.change.actions[_] == "create"
	resource.change.after.server_side_encryption
}


# Allow if DynamoDB table is modified and stream is configured correctly
allow if {
	dynamodb_table_modified(input.resource_changes)
}
