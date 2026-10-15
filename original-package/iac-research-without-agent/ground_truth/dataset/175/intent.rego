package main

import rego.v1

default allow := false

aws_sagemaker_domain_valid(resources) if {
	some resource in resources
	resource.type == "aws_sagemaker_domain"
}

aws_iam_role_valid(resources) if {
	some resource in resources
	resource.type == "aws_iam_role"
}

aws_vpc_valid(resources) if {
	some resource in resources
	resource.type == "aws_vpc"
}

aws_subnet_valid(resources) if {
	some resource in resources
	resource.type == "aws_subnet"
}

aws_sagemaker_user_profile_valid(resources) if {
	some resource in resources
	resource.type == "aws_sagemaker_user_profile"
}

aws_sagemaker_app_valid(resources) if {
	some resource in resources
	resource.type == "aws_sagemaker_app"
}

# Aggregate all checks
allow if {
	aws_sagemaker_domain_valid(input.resource_changes)
	aws_iam_role_valid(input.resource_changes)
	aws_vpc_valid(input.resource_changes)
	aws_subnet_valid(input.resource_changes)
	aws_sagemaker_user_profile_valid(input.resource_changes)
	aws_sagemaker_app_valid(input.resource_changes)
}
