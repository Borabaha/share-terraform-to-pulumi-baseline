package main

import rego.v1

default allow := false

aws_elasticache_cluster_valid(resources) if {
	some resource in resources
	resource.type == "aws_elasticache_cluster"
	resource.change.after.engine == "redis"
}

# Aggregate all checks
allow if {
	aws_elasticache_cluster_valid(input.resource_changes)
}
