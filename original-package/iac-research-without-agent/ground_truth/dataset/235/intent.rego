package vpc_egress_netgate

import rego.v1

default valid := false

valid if {
	some eg_ig_resource in input.configuration.root_module.resources
	eg_ig_resource.type == "aws_egress_only_internet_gateway"

	some vpc_resource in input.configuration.root_module.resources
	vpc_resource.type == "aws_vpc"
	vpc_resource.address in eg_ig_resource.expressions.vpc_id.references
}
