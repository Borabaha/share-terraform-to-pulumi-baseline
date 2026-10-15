package main

import rego.v1

default allow := false

# Check if AWS ElastiCache user group exists
aws_elasticache_user_group_exists(resources) if {
	some resource in resources
	resource.type == "aws_elasticache_user_group"
	resource.change.actions[_] == "create"
	count(resource.change.after[user_ids]) == 3
}

# Check if AWS ElastiCache user exists
aws_elasticache_user_exists(resources) if {
	some resource in resources
	resource.type == "aws_elasticache_user"
	resource.change.actions[_] == "create"
}

# Aggregate all checks
allow if {
	aws_elasticache_user_group_exists(input.resource_changes)
	aws_elasticache_user_exists(input.resource_changes)
}
