package main

import rego.v1

default allow := false

# Check if AWS CloudWatch Composite Alarm is being created
aws_cloudwatch_composite_alarm_valid(resources) if {
	some resource in resources
	resource.type == "aws_cloudwatch_composite_alarm"
}

# Aggregate all checks
allow if {
	aws_cloudwatch_composite_alarm_valid(input.resource_changes)
}
