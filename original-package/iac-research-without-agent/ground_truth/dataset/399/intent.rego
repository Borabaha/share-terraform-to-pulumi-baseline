package terraform.validation

import rego.v1

default is_valid_configuration := false

# has one asw_lb resource
is_valid_lb if {
	is_valid_app_lb
	has_valid_subnet
}

is_valid_app_lb if {
	resource := input.planned_values.root_module.resources[_]
	resource.type == "aws_lb"
	resource.values.load_balancer_type == "application"
}

has_valid_subnet if {
	resource := input.planned_values.root_module.resources[_]
	resource.type == "aws_lb"
	resource.values.subnet_mapping != null
}

has_valid_subnet if {
	resource := input.configuration.root_module.resources[_]
	resource.type == "aws_lb"
	resource.expressions.subnets
}

# has one vpc resource
is_valid_vpc if {
	have_required_vpc_argument
}

have_required_vpc_argument if {
	resource := input.configuration.root_module.resources[_]
	resource.type == "aws_vpc"
	resource.expressions.cidr_block.constant_value != null
}

have_required_vpc_argument if {
	resource := input.configuration.root_module.resources[_]
	resource.type == "aws_vpc"
	resource.expressions.ipv4_ipam_pool_id.constant_value != null
}

# has valid subnet
is_valid_subnet if {
	resource := input.configuration.root_module.resources[_]
	resource.type == "aws_subnet"
	resource.expressions.vpc_id != null
	have_required_subnet_argument
}

have_required_subnet_argument if {
	resource := input.configuration.root_module.resources[_]
	resource.type == "aws_subnet"
	resource.expressions.cidr_block != null
}

have_required_subnet_argument if {
	resource := input.configuration.root_module.resources[_]
	resource.type == "aws_subnet"
	resource.expressions.ipv6_cider_block != null
}




# Aggregate validation
is_valid_configuration if {
	is_valid_vpc
	is_valid_subnet
	is_valid_lb
}
