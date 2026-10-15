package iam_user_basic

import rego.v1

default valid := false

valid if {
	some user_resource in input.configuration.root_module.resources
	user_resource.type == "aws_iam_user"
}
