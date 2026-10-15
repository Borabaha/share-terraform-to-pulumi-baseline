package terraform.validation

import rego.v1

default is_configuration_valid := false

default is_valid_iam_instance_profile := false

default is_valid_iam_role := false

default is_valid_eb_app := false

default is_valid_eb_env := false

is_valid_iam_role if {
	some i
	resource := input.resource_changes[i]
	resource.type == "aws_iam_role"
	contains(resource.change.after.assume_role_policy, "ec2.amazonaws.com")
}


# Validate aws_iam_instance_profile resource
is_valid_iam_instance_profile if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_iam_instance_profile"
	resource.expressions.role.references[0] == "aws_iam_role.eb_ec2_role.name"
}

# Validate aws_eb_app
is_valid_eb_app if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_elastic_beanstalk_application"
	resource.expressions.name
}

# Validate aws_eb_env
is_valid_eb_env if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_elastic_beanstalk_environment"
	resource.expressions.name
	resource.expressions.application.references[0]
	resource.expressions.solution_stack_name
	resource.expressions.tier.constant_value == "WebServer"
	resource.expressions.setting[0].value.references[0]
}

# Combine all checks into a final rule
is_configuration_valid if {
	is_valid_iam_role
	is_valid_iam_instance_profile
	is_valid_eb_app
	is_valid_eb_env
}
