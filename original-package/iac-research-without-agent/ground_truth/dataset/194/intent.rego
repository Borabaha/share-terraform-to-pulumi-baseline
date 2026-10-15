package main

import rego.v1

default allow := false

aws_elasticache_user_valid(resources) if {
	some resource in resources
	resource.type == "aws_elasticache_user"
	resource.change.after.engine == "redis"
}

# Aggregate all checks
allow if {
	aws_elasticache_user_valid(input.resource_changes)
}
