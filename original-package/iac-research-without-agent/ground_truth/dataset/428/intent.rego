package terraform.validation

import rego.v1

default is_valid_subnet := false

default is_valid_internet_gateway := false

default is_valid_route_table := false

default is_valid_route_table_association := false

# Validate aws_subnet resource
is_valid_subnet if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_subnet"
	resource.expressions.vpc_id.references != null
	resource.expressions.cidr_block != null
}

# Validate aws_internet_gateway resource
is_valid_internet_gateway if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_internet_gateway"
	resource.expressions.vpc_id.references != null
}

# Validate aws_route_table resource
is_valid_route_table if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_route_table"
	resource.expressions.vpc_id.references != null
	resource.expressions.route != null
	#resource.expressions.tags != null
}

# Validate aws_route_table_association resource
is_valid_route_table_association if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_route_table_association"
	resource.expressions.subnet_id.references != null
	resource.expressions.route_table_id.references != null
}
