package terraform.validation

import rego.v1

default has_valid_lightsail_disk := false

# Rule for aws_lightsail_disk resource with specific arguments
has_valid_lightsail_disk if {
	some i
	resource := input.planned_values.root_module.resources[i]
	resource.type == "aws_lightsail_disk"
	resource.values.name
	resource.values.size_in_gb
	resource.values.availability_zone
}
