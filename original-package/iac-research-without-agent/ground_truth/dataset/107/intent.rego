package terraform.validation

import rego.v1

default has_s3_bucket_versioning := false

default has_s3_bucket := false

default valid_configuration := false

has_s3_bucket if {
	resource := input.configuration.root_module.resources[_]
	resource.type == "aws_s3_bucket"
	resource.name == "sample"
}

has_s3_bucket_versioning if {
	versioning := input.planned_values.root_module.resources[_]
	versioning.type == "aws_s3_bucket_versioning"
	#versioning.values.bucket
	versioning.values.expected_bucket_owner == "123456789012"
	versioning.values.versioning_configuration[_].status == "Enabled"
}

valid_configuration if {
	has_s3_bucket
	has_s3_bucket_versioning
}
