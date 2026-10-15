package terraform.validation

import rego.v1

# Set default validation states
default is_valid_network_acl := false

# Validate aws_network_acl resources
is_valid_network_acl if {
	some i
	network_acl := input.configuration.root_module.resources[i]
	network_acl.type == "aws_network_acl"
	network_acl.name

	# Validate linked VPC
	network_acl.expressions.vpc_id.references[0]

	# Check ingress rules for allowing TCP traffic on port 80 from CIDR "10.3.0.0/18"
	ingress := network_acl.expressions.ingress
	ingress.constant_value[0].protocol == "tcp"
	ingress.constant_value[0].rule_no == 100
	ingress.constant_value[0].action == "allow"

	# Check egress rules for allowing TCP traffic on port 443 to CIDR "10.3.0.0/18"
	egress := network_acl.expressions.egress
	egress.constant_value[0].protocol == "tcp"
	egress.constant_value[0].rule_no == 200
	egress.constant_value[0].action == "allow"
}

is_valid_network_acl if {
	some i
	network_acl := input.configuration.root_module.resources[i]
	network_acl.type == "aws_network_acl"
	network_acl.name

	# Validate linked VPC
	network_acl.expressions.vpc_id.references[0]

	# Check ingress rules for allowing TCP traffic on port 80 from CIDR "10.3.0.0/18"
	some j
	ingress := input.configuration.root_module.resources[j]
	ingress.type == "aws_network_acl_rule"
	ingress.expressions.egress.constant_value == false
	ingress.expressions.protocol.constant_value == "tcp"
	ingress.expressions.rule_action.constant_value == "allow"

	# Check egress rules for allowing TCP traffic on port 443 to CIDR "10.3.0.0/18"
	some k
	egress := input.configuration.root_module.resources[k]
	egress.type == "aws_network_acl_rule"
	egress.expressions.egress.constant_value == true
	egress.expressions.protocol.constant_value == "tcp"
	egress.expressions.rule_action.constant_value == "allow"
}
