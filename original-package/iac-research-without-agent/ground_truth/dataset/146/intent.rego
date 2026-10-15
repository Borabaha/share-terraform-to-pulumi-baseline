package main

import rego.v1

default allow := false

aws_redshift_cluster_valid(resources) if {
	some resource in resources
	resource.type == "aws_redshift_cluster"
	resource.change.after.number_of_nodes == 1
}

iam_role_vaild(resources) if {
	some resource in resources
	resource.type == "aws_iam_role"
}

aws_iam_role_policy_attachment(resources) if {
	some resource in resources
	resource.type == "aws_iam_role_policy_attachment"
}

aws_redshift_cluster_iam_roles_valid(resources) if {
	some resource in resources
	resource.type == "aws_redshift_cluster_iam_roles"
}

# Aggregate all checks
allow if {
	aws_redshift_cluster_valid(input.resource_changes)
	iam_role_vaild(input.resource_changes)
	aws_iam_role_policy_attachment(input.resource_changes)
	aws_redshift_cluster_iam_roles_valid(input.resource_changes)
}
