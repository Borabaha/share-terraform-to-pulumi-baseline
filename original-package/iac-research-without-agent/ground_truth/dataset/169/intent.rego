package main

import rego.v1

default allow := false

# Check if the AWS DynamoDB table is being created in us-east-1
aws_dax_parameter_group_valid(resources) if {
	some resource in resources
	resource.type == "aws_dax_parameter_group"
}

# Aggregate all checks
allow if {
	aws_dax_parameter_group_valid(input.resource_changes)
}
