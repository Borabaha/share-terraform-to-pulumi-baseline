package terraform.validation

import rego.v1

default is_configuration_valid := false

default is_valid_r53_zone := false

default is_valid_r53_record_primary := false

default is_valid_r53_record_secondary := false

default is_valid_r53_health_check := false

# Validate aws_route53_zone resource
is_valid_r53_zone if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_route53_zone"
}

# Validate aws_route53_record
is_valid_r53_record_primary if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_route53_record"
	resource.expressions.name
	resource.expressions.name.constant_value == "primary"
	resource.expressions.type
	resource.expressions.ttl
	resource.expressions.records
	resource.expressions.zone_id.references[0]
	resource.expressions.health_check_id.references[0]
}

is_valid_r53_record_secondary if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_route53_record"
	resource.expressions.name
	resource.expressions.name.constant_value == "secondary"
	resource.expressions.type
	resource.expressions.ttl
	resource.expressions.records
	resource.expressions.zone_id.references[0]
}

# Validate aws_route53_health_check
is_valid_r53_health_check if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_route53_health_check"
	resource.name == "primary_health_check"
	resource.expressions.fqdn
	#resource.expressions.request_interval
	resource.expressions.type
}

# Combine all checks into a final rule
is_configuration_valid if {
	is_valid_r53_health_check
	is_valid_r53_zone
	is_valid_r53_record_primary
	is_valid_r53_record_secondary
}
