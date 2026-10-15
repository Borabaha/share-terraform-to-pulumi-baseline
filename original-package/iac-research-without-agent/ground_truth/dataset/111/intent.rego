package terraform.validation

import rego.v1

default has_s3_bucket := false

default has_s3_bucket_object_lock_configuration := false

default valid_configuration := false

has_s3_bucket if {
	bucket := input.planned_values.root_module.resources[_]
	bucket.type == "aws_s3_bucket"
	bucket.name
}

has_s3_bucket_object_lock_configuration if {
	lock_config := input.planned_values.root_module.resources[_]
	lock_config.type == "aws_s3_bucket_object_lock_configuration"
	#lock_config.values.bucket
	default_retention := lock_config.values.rule[_].default_retention[_]
	default_retention.mode == "GOVERNANCE"
	default_retention.days == 90
}

valid_configuration if {
	has_s3_bucket
	has_s3_bucket_object_lock_configuration
}
