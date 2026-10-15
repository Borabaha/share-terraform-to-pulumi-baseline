package terraform.validation

import rego.v1

default is_configuration_valid := false

default is_valid_eb_app := false

default is_valid_eb_app_template := false

is_valid_eb_app if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_elastic_beanstalk_application"
	resource.expressions.name
}

is_valid_eb_app_template if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_elastic_beanstalk_configuration_template"
	resource.expressions.name
	endswith(resource.expressions.solution_stack_name.constant_value, "Go 1")
	startswith(resource.expressions.application.references[0], "aws_elastic_beanstalk_application")
}

is_configuration_valid if {
	is_valid_eb_app
	is_valid_eb_app_template
}
