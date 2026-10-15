package main

import rego.v1

default allow := false

dynamodb_table_modified(resources) if {
	some resource in resources
	resource.type == "aws_dynamodb_table"
	resource.change.actions[_] == "create"
}

encryption_at_rest_enabled(resource) if {
	resource.type == "aws_dynamodb_table"
	resource.change.after.server_side_encryption[_].enabled == true
}

allow if {
	dynamodb_table_modified(input.resource_changes)
	some resource in input.resource_changes
	encryption_at_rest_enabled(resource)
}
