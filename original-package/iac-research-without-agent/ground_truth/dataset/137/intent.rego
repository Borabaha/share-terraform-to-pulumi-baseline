package main

import rego.v1

default allow := false

aws_elasticache_user_group_valid(resources) if {
	some resource in resources
	resource.type == "aws_elasticache_user_group"
}

# Aggregate all checks
allow if {
	aws_elasticache_user_group_valid(input.resource_changes)
}
