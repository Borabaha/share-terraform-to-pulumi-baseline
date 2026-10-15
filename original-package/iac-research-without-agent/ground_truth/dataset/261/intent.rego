package iam_group_two_users

import rego.v1

default valid := false

valid if {
	some user1 in input.configuration.root_module.resources
	user1.type == "aws_iam_user"

	some user2 in input.configuration.root_module.resources
	user2.type == "aws_iam_user"

	not user1 == user2

	some group in input.configuration.root_module.resources
	group.type == "aws_iam_group"

	some group_membership in input.configuration.root_module.resources
	group_membership.type == "aws_iam_group_membership"
	user1.address in group_membership.expressions.users.references
	user2.address in group_membership.expressions.users.references
	group.address in group_membership.expressions.group.references
}
