package main

import rego.v1

default allow := false

# Check for DAX parameter group creation
dax_parameter_group_created(resources) if {
	some resource in resources
	resource.type == "aws_dax_parameter_group"
	resource.change.actions[_] == "create"
}

# Allow DAX parameter group creation with specific parameters
allow if {
	dax_parameter_group_created(input.resource_changes)
}
