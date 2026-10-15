package terraform.validation

import rego.v1

default is_valid_vpc := false

default is_valid_subnet := false

default is_valid_lb := false

default is_valid_security_group := false

# has one asw_lb resource
is_valid_lb if {
	is_valid_app_lb
	has_valid_subnet
	has_valid_lb_argument
}

is_valid_app_lb if {
	resource := input.planned_values.root_module.resources[_]
	resource.type == "aws_lb"
	resource.values.load_balancer_type == "application"
}

has_valid_subnet if {
	resource := input.configuration.root_module.resources[_]
	resource.type == "aws_lb"
	resource.expressions.subnets
}

has_valid_lb_argument if {
	resource := input.configuration.root_module.resources[_]
	resource.type == "aws_lb"
	resource.expressions.enable_deletion_protection.constant_value == true
	resource.expressions.internal.constant_value == false
	resource.expressions.name.constant_value == "test-lb-tf"
	resource.expressions.security_groups.references != null
}

# has one vpc resource
is_valid_vpc if {
	resource := input.configuration.root_module.resources[_]
	resource.expressions.cidr_block.constant_value != null
}

# has valid subnet
is_valid_subnet if {
	resource := input.configuration.root_module.resources[_]
	resource.type == "aws_subnet"
	resource.expressions.vpc_id != null
	resource.expressions.cidr_block != null
}


requited_argument(instance) if {
	instance.expressions.ami != null
	instance.expressions.instance_type != null
}

is_valid_security_group if {
	resource := input.configuration.root_module.resources[_]
	resource.type == "aws_security_group"
}

# Aggregate validation
is_valid_configuration if {
	is_valid_vpc
	is_valid_subnet
	is_valid_lb
	is_valid_security_group
}
