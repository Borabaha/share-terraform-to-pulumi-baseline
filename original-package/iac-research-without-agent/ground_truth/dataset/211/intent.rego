package main

import rego.v1

default allow := false

# Check if an MSK serverless cluster is being created
msk_serverless_cluster_created(resources) if {
	some resource in resources
	resource.type == "aws_msk_serverless_cluster"
	resource.change.actions[_] == "create"
}

# Check if the cluster is in us-east-1 using provider config
msk_cluster_region_valid(resource) if {
	input.configuration.provider_config.aws.expressions.region.constant_value == "us-east-2"
}

# Aggregate all checks
allow if {
	msk_serverless_cluster_created(input.resource_changes)
	some resource in input.resource_changes
	msk_cluster_region_valid(resource)
}
