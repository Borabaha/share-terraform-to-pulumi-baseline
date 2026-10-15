package main

import rego.v1

default allow := false

# Check for DynamoDB table creation or update
dynamodb_table_modified(resources) if {
	some resource in resources
	resource.type == "aws_dynamodb_table"
	resource.change.actions[_] == "create"
}

# Check if point-in-time recovery is enabled
point_in_time_recovery_enabled(resource) if {
	resource.type == "aws_dynamodb_table"
	resource.change.after.point_in_time_recovery[_].enabled == true
}

# Allow if DynamoDB table is modified and point-in-time recovery is enabled
allow if {
	dynamodb_table_modified(input.resource_changes)
	some resource in input.resource_changes
	point_in_time_recovery_enabled(resource)
}
