package terraform.validation

import rego.v1

default has_valid_lightsail_certificate := false

# Rule for aws_lightsail_certificate resource with specific arguments
has_valid_lightsail_certificate if {
	some i
	resource := input.planned_values.root_module.resources[i]
	resource.type == "aws_lightsail_certificate"
	resource.values.name
	resource.values.domain_name
}
