package main

import rego.v1

default allow := false

aws_elasticache_user_valid(resources) if {
	some resource in resources
	resource.type == "aws_elasticache_user"
	resource.change.after.authentication_mode[_].type == "password"
}

aws_elasticache_user_valid(resources) if {
	some resource in resources
	resource.type == "aws_elasticache_user"
	resource.change.after.passwords
}

# Aggregate all checks
allow if {
	aws_elasticache_user_valid(input.resource_changes)
}
