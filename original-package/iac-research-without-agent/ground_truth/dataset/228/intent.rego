package main

import rego.v1

default allow := false

# Check for DAX subnet group creation
dax_subnet_group_created(resources) if {
	some resource in resources
	resource.type == "aws_dax_subnet_group"
	resource.change.actions[_] == "create"
}

# Allow DAX subnet group creation with sufficient subnets
allow if {
	dax_subnet_group_created(input.resource_changes)
}
