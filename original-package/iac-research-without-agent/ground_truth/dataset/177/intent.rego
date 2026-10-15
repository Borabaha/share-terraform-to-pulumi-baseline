package main

import rego.v1

default allow := false

aws_iam_role_valid(resources) if {
	some resource in resources
	resource.type == "aws_iam_role"
}

aws_sagemaker_image_valid(resources) if {
	some resource in resources
	resource.type == "aws_sagemaker_image"
}

# Aggregate all checks
allow if {
	aws_sagemaker_image_valid(input.resource_changes)
	aws_iam_role_valid(input.resource_changes)
}
