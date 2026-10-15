package main

import rego.v1

default allow := false

# Check if MSK cluster is serverless
is_serverless(resource) if {
	resource.type == "aws_msk_serverless_cluster"
}

# Check if cluster spans three AZs
has_three_azs(resource) if {
	resource.type == "aws_msk_serverless_cluster"
	count(resource.expressions.vpc_config[_].subnet_ids.references) >= 3
}

msk_cluster_region_valid(resource) if {
	input.configuration.provider_config.aws.expressions.region.constant_value == "us-east-1"
}

# Main rule combining all checks
allow if {
	some resource in input.configuration.root_module.resources
	is_serverless(resource)
	has_three_azs(resource)
	msk_cluster_region_valid(resource)
}
