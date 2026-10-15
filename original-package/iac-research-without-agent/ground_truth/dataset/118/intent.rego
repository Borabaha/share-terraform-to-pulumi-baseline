package terraform.validation

import rego.v1

default has_aws_s3_bucket := false

default has_aws_s3_bucket_versioning := false

default has_aws_s3_bucket_object_lock_configuration := false

has_aws_s3_bucket if {
	bucket := input.planned_values.root_module.resources[_]
	bucket.type == "aws_s3_bucket"
	bucket.name == "mybucket"
	bucket.values.bucket == "mybucket"
}

has_aws_s3_bucket_versioning if {
	versioning := input.planned_values.root_module.resources[_]
	versioning.type == "aws_s3_bucket_versioning"
	versioning.name
	
	#versioning.values.bucket == input.planned_values.root_module.resources[_].values.id # Correct bucket ID reference
	count(versioning.values.versioning_configuration) > 0
	versioning.values.versioning_configuration[0].status == "Enabled"
}

has_aws_s3_bucket_object_lock_configuration if {
	lock_config := input.planned_values.root_module.resources[_]
	lock_config.type == "aws_s3_bucket_object_lock_configuration"
	lock_config.name
	#lock_config.values.bucket == input.planned_values.root_module.resources[_].values.id # Correct bucket ID reference
	lock_config.values.rule[0].default_retention[0].mode == "COMPLIANCE"
	lock_config.values.rule[0].default_retention[0].days == 5
}

valid_configuration if {
	has_aws_s3_bucket
	has_aws_s3_bucket_versioning
	has_aws_s3_bucket_object_lock_configuration
}
