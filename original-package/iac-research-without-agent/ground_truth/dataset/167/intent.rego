package main

import rego.v1

default allow := false

# Check if the AWS DynamoDB table is being created in us-east-1
aws_dynamodb_table(resources) if {
	some resource in resources
	resource.type == "aws_dynamodb_table"
}

# Check if the AWS DynamoDB table replica is being created in us-east-2
aws_dynamodb_table_replica(resources) if {
	some resource in resources
	resource.type == "aws_dynamodb_table_replica"
}

aws_dynamodb_table_replica(resources) if {
	some resource in resources
	resource.type == "aws_dynamodb_table"
	resource.change.after.replica
}

# Aggregate all checks
allow if {
	aws_dynamodb_table(input.resource_changes)
	aws_dynamodb_table_replica(input.resource_changes)
}
