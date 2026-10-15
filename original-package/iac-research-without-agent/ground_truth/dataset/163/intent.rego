package main

import rego.v1

default allow := false

# Check if AWS DynamoDB Global Table is being created with replicas in specific regions
aws_dynamodb_global_table_valid(resources) if {
	some resource in resources
	resource.type == "aws_dynamodb_table"
	resource.change.actions[_] == "create"
	resource.change.after.name == "myTable"
	count(resource.change.after.replica) == 2
	resource.change.after.replica[_].region_name == "us-west-1"
	resource.change.after.replica[_].region_name == "us-west-2"
}

# Aggregate all checks
allow if {
	aws_dynamodb_global_table_valid(input.resource_changes)
}
