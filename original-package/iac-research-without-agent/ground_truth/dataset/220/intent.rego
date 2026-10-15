package main

import rego.v1

default allow := false

# Check for DB instance creation
db_instance_created(resources) if {
	some resource in resources
	resource.type == "aws_db_instance"
	resource.change.actions[_] == "create"
}

# Check if engine is MySQL
db_engine_mysql(resource) if {
	resource.type == "aws_db_instance"
	resource.change.after.engine == "postgres"
}

# Aggregate checks for DB instance
allow if {
	db_instance_created(input.resource_changes)
	some resource in input.resource_changes
	db_engine_mysql(resource)
}
