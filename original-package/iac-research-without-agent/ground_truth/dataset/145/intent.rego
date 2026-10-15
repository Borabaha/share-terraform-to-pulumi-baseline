package main

import rego.v1

default allow := false

aws_redshift_cluster_valid(resources) if {
	some resource in resources
	resource.type == "aws_redshift_cluster"
	resource.change.after.number_of_nodes == 2
	#resource.change.after.snapshot_copy[_].destination_region == "us-east-2"
}

# Aggregate all checks
allow if {
	aws_redshift_cluster_valid(input.resource_changes)
}
