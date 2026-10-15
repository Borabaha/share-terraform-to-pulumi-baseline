package main

import rego.v1

default allow := false


aws_instances contains resource if {
	resource := input.resource_changes[_]
	resource.type == "aws_instance"
}

# Aggregate all checks
allow if {
	count(aws_instances) == 3
}
