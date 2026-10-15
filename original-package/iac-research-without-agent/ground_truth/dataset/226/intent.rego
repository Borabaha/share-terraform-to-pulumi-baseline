package main

import rego.v1

default allow := false

# Check for DAX cluster creation
dax_cluster_created(resources) if {
	some resource in resources
	resource.type == "aws_dax_cluster"
	resource.change.actions[_] == "create"
}

# Allow DAX cluster creation
allow if {
	dax_cluster_created(input.resource_changes)
}
