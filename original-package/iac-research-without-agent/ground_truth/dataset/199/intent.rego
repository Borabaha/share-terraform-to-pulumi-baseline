package main

import rego.v1

default allow := false

# Check if the AWS DynamoDB table is being created in us-east-1
aws_dax_cluster_valid(resources) if {
	some resource in resources
	resource.type == "aws_dax_cluster"
	resource.change.after.node_type == "dax.r4.large"
	resource.change.after.replication_factor == 1
}

# Aggregate all checks
allow if {
	aws_dax_cluster_valid(input.resource_changes)
}
