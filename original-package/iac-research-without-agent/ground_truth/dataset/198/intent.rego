package main

import rego.v1

default allow := false

# Check if AWS DynamoDB Contributor Insights is being created for a specific table
aws_dynamodb_contributor_insights_valid(resources) if {
	some resource in resources
	resource.type == "aws_dynamodb_contributor_insights"
}

# Aggregate all checks
allow if {
	aws_dynamodb_contributor_insights_valid(input.resource_changes)
}
