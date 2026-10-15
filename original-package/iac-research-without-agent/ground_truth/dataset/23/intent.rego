package terraform.validation

import rego.v1

default is_configuration_valid := false

default is_valid_r53_zone := false

default is_valid_r53_record := false

# Validate aws_route53_zone resource
is_valid_r53_zone if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_route53_zone"
}

# Validate aws_route53_record
is_valid_r53_record if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_route53_record"
	resource.expressions.name
	resource.expressions.type.constant_value == "TXT"
	resource.expressions.ttl
	resource.expressions.records.constant_value[0] == "passwordpassword"
	resource.expressions.zone_id.references[0]
}

# Combine all checks into a final rule
is_configuration_valid if {
	is_valid_r53_zone
	is_valid_r53_record
}
