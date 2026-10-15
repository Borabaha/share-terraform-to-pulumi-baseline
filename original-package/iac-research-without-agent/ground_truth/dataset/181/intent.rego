package main

import rego.v1

default allow := false

aws_iam_role_valid(resources) if {
	some resource in resources
	resource.type == "aws_iam_role"
}

aws_sagemaker_pipeline_valid(resources) if {
	some resource in resources
	resource.type == "aws_sagemaker_pipeline"
}

# Aggregate all checks
allow if {
	aws_iam_role_valid(input.resource_changes)
	aws_sagemaker_pipeline_valid(input.resource_changes)
}
