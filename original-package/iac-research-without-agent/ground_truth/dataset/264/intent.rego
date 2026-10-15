package iam_group_basic

import rego.v1

default valid := false

valid if {
	some group_resource in input.configuration.root_module.resources
	group_resource.type == "aws_iam_group"
}
