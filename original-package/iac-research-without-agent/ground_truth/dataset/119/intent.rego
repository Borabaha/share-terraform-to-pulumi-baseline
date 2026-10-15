package terraform.validation

import rego.v1

default has_aws_kms_key := false

default has_aws_s3_bucket := false

default has_aws_s3_bucket_server_side_encryption_configuration := false

has_aws_kms_key if {
	key := input.planned_values.root_module.resources[_]
	key.type == "aws_kms_key"
	#key.name == "mykey"
	key.values.description != null
	key.values.deletion_window_in_days != null
}

has_aws_s3_bucket if {
	bucket := input.planned_values.root_module.resources[_]
	bucket.type == "aws_s3_bucket"
	bucket.values.bucket != null
}

has_aws_s3_bucket_server_side_encryption_configuration if {
	encryption_config := input.planned_values.root_module.resources[_]
	encryption_config.type == "aws_s3_bucket_server_side_encryption_configuration"
	encryption_config.name == "example"
	#encryption_config.values.bucket == input.planned_values.root_module.resources[_].values.id # Correct bucket ID reference
	#rule := encryption_config.values.rule.apply_server_side_encryption_by_default
	#encryption_config.values.rule[0].apply_server_side_encryption_by_default[0].kms_master_key_id == "aws_kms_key.mykey"
	encryption_config.values.rule[_].apply_server_side_encryption_by_default[_].sse_algorithm == "aws:kms"
}

valid_configuration if {
	has_aws_kms_key
	has_aws_s3_bucket
	has_aws_s3_bucket_server_side_encryption_configuration
}
