package main

import rego.v1

default allow := false

aws_redshift_cluster_valid(resources) if {
	some resource in resources
	resource.type == "aws_redshift_cluster"
	resource.change.after.number_of_nodes == 1
}

# Function to check if Redshift snapshot schedule is every 12 hours
aws_redshift_snapshot_schedule_valid(resources) if {
	some resource in resources
	resource.type == "aws_redshift_snapshot_schedule"
	resource.change.after.definitions[_] == "rate(12 hours)"
}

# Aggregate all checks
allow if {
	aws_redshift_cluster_valid(input.resource_changes)
	aws_redshift_snapshot_schedule_valid(input.resource_changes)
}
