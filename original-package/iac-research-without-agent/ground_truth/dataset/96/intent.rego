package terraform.validation

import rego.v1

default has_aws_iam_role_example := false

default has_aws_iam_role_policy_attachment_example := false

has_aws_iam_role_example if {
	role := input.planned_values.root_module.resources[_]
	role.type == "aws_iam_role"
	role.values.name == "eks-fargate-profile-example"

	# Ensure the assume role policy is correctly configured
	role.values.assume_role_policy
}

has_aws_iam_role_policy_attachment_example if {
	attachment := input.planned_values.root_module.resources[_]
	attachment.type == "aws_iam_role_policy_attachment"
	attachment.name
	attachment.values.policy_arn == "arn:aws:iam::aws:policy/AmazonEKSFargatePodExecutionRolePolicy"

	# Check if the role is correctly referenced
	attachment.values.role == input.planned_values.root_module.resources[_].values.name
}

has_aws_iam_role_policy_attachment_example if {
	attachment := input.planned_values.root_module.resources[_]
	attachment.type == "aws_iam_policy_attachment"
	attachment.name
	attachment.values.policy_arn == "arn:aws:iam::aws:policy/AmazonEKSFargatePodExecutionRolePolicy"
}

valid_configuration if {
	has_aws_iam_role_example
	has_aws_iam_role_policy_attachment_example
}
