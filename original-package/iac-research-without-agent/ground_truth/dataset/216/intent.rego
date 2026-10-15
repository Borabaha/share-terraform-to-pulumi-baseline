package main

import rego.v1

default allow := false

# Check for Aurora MySQL RDS cluster creation
rds_cluster_created(resources) if {
	some resource in resources
	resource.type == "aws_rds_cluster"
	resource.change.actions[_] == "create"
}

# Check if the RDS cluster engine is Aurora MySQL
rds_cluster_engine_valid(resource) if {
	resource.type == "aws_rds_cluster"
	resource.change.after.engine == "aurora-postgresql"
}

# Aggregate checks for Aurora MySQL RDS
allow if {
	# RDS Cluster Checks
	rds_cluster_created(input.resource_changes)
	some resource in input.resource_changes
	rds_cluster_engine_valid(resource)
}
