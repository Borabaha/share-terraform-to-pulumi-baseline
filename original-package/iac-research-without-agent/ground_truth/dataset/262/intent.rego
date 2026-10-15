package iam_group_policy_attachment

import rego.v1

default valid := false

valid if {
	some group_attachment in input.configuration.root_module.resources
	group_attachment.type == "aws_iam_group_policy_attachment"

	some group in input.configuration.root_module.resources
	group.type == "aws_iam_group"
	group.address in group_attachment.expressions.group.references

	some policy in input.configuration.root_module.resources
	policy.type == "aws_iam_policy"
	policy.address in group_attachment.expressions.policy_arn.references
}
