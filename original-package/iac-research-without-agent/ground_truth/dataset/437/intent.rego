package terraform.validation

import rego.v1

# Set default validation states
default is_valid_vpc := false

default is_valid_internet_gateway := false

default is_valid_route_table := false

default is_valid_subnets1 := false

default is_valid_subnets2 := false

default is_valid_security_group := false

default is_valid_db_subnet_group := false

# Validate aws_vpc resource
is_valid_vpc if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_vpc"
	resource.expressions.cidr_block.constant_value != null
}

# Validate aws_subnet resources
is_valid_subnets1 if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_subnet"
	resource.expressions.vpc_id.references[0]
	#resource.expressions.availability_zone.constant_value == "us-west-1a"
}

is_valid_subnets2 if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_subnet"
	resource.expressions.vpc_id.references[0]
	#resource.expressions.availability_zone.constant_value == "us-west-1b"
}

# Validate aws_internet_gateway resource
is_valid_internet_gateway if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_internet_gateway"
	resource.expressions.vpc_id.references[0]
}

# Validate aws_route_table resource
is_valid_route_table if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_route_table"
	resource.expressions.vpc_id.references[0]
	#resource.expressions.route.references[0]
}

# Validate aws_security_group resource
is_valid_security_group if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_security_group"
	resource.expressions.vpc_id.references[0]
	some j
	port1 := resource.expressions.ingress.constant_value[j]
	port1.from_port == 3306
	some k
	port2 := resource.expressions.ingress.constant_value[k]
	port2.from_port == 5432
}

# Validate aws_db_subnet_group resource
is_valid_db_subnet_group if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_db_subnet_group"
}
