package main

import rego.v1

default allow := false

aws_redshift_cluster_valid(resources) if {
	some resource in resources
	resource.type == "aws_redshift_cluster"
	resource.change.after.number_of_nodes == 2
}

aws_redshift_usage_limit_valid(resources) if {
	some resource in resources
	resource.type == "aws_redshift_usage_limit"
	resource.change.after.feature_type == "concurrency-scaling"
	resource.change.after.limit_type == "time"
	resource.change.after.amount == 60
}

# Aggregate all checks
allow if {
	aws_redshift_cluster_valid(input.resource_changes)
	aws_redshift_usage_limit_valid(input.resource_changes)
}
