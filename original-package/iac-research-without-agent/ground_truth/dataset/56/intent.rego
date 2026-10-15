package terraform.validation

import rego.v1

default has_valid_resources := false

has_valid_kinesis_stream if {
	resource := input.planned_values.root_module.resources[i]
	resource.type == "aws_kinesis_stream"
	resource.values.name
}

has_valid_resources if {
	has_valid_kinesis_stream
}
