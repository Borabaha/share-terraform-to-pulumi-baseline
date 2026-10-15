package terraform.validation

import rego.v1

default is_configuration_valid := false

default is_valid_eb_app := false

is_valid_eb_app if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_elastic_beanstalk_application"
	resource.expressions.name
}

is_configuration_valid if {
	is_valid_eb_app
}
