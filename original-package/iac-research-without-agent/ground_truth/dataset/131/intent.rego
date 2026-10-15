package main

import rego.v1

default allow := false

# Check for VPC with public and private subnets
vpc_exists if {
	some i
	input.resource_changes[i].type == "aws_vpc"
}

public_subnet_exists(resources) if {
	some resource in resources
	resource.type == "aws_subnet"
	resource.change.after.map_public_ip_on_launch == true
}

private_subnet_exists(resources) if {
	some resource in resources
	resource.type == "aws_subnet"
	resource.change.after.map_public_ip_on_launch == false
}

aws_instances contains resource if {
	resource := input.resource_changes[_]
	resource.type == "aws_instance"
}

# Aggregate all checks
allow if {
	vpc_exists
	public_subnet_exists(input.resource_changes)
	private_subnet_exists(input.resource_changes)
	count(aws_instances) == 3
}
