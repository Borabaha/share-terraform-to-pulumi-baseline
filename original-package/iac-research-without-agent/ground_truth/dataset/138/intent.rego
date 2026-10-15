package main

import rego.v1

default allow := false

# Check if AWS ElastiCache user group exists
aws_elasticache_user_group_exists(resources) if {
	some resource in resources
	resource.type == "aws_elasticache_user_group"
	resource.change.actions[_] == "create"
}

# Check if AWS ElastiCache user exists
aws_elasticache_user_exists(resources) if {
	some resource in resources
	resource.type == "aws_elasticache_user"
	resource.change.actions[_] == "create"
}

# Check if AWS ElastiCache user group association is valid
aws_elasticache_user_group_association_valid(resources) if {
	aws_elasticache_user_exists(resources)
	aws_elasticache_user_group_exists(resources)

	some resource in resources
	resource.type == "aws_elasticache_user_group_association"
	resource.change.actions[_] == "create"
	user_id := resource.change.after.user_id
	group_id := resource.change.after.user_group_id

	user_id_exists(user_id, resources)
	group_id_exists(group_id, resources)
}

# Helper functions to check if user_id and group_id exist in the resources
user_id_exists(user_id, resources) if {
	some resource in resources
	resource.type == "aws_elasticache_user"
	resource.change.after.user_id == user_id
}

group_id_exists(group_id, resources) if {
	some resource in resources
	resource.type == "aws_elasticache_user_group"
	resource.change.after.user_group_id == group_id
}

# Aggregate all checks
allow if {
	aws_elasticache_user_group_association_valid(input.resource_changes)
}
