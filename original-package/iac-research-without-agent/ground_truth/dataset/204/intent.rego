package main

import rego.v1

default allow := false

# Check if any MSK cluster is being created
msk_cluster_created(resources) if {
	some resource in resources
	resource.type == "aws_msk_cluster"
	resource.change.actions[_] == "create"
}

# Check if S3 logging is enabled for broker logs
s3_logging_enabled(resource) if {
	resource.type == "aws_msk_cluster"
	resource.change.after.logging_info[_].broker_logs[_].s3[_].enabled == true
}

# Aggregate all checks
allow if {
	msk_cluster_created(input.resource_changes)
	some resource in input.resource_changes
	s3_logging_enabled(resource)
}
