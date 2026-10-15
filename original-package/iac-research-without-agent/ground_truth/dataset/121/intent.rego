package terraform.validation

import rego.v1

default has_aws_s3_bucket_example := false

default has_aws_s3_bucket_acl_example := false

default has_aws_s3_bucket_log := false

default has_aws_s3_bucket_acl_log := false

default has_aws_s3_bucket_logging_example := false

has_aws_s3_bucket_example if {
	bucket := input.planned_values.root_module.resources[_]
	bucket.type == "aws_s3_bucket"
	bucket.values.bucket
}

has_aws_s3_bucket_acl_example if {
	acl := input.planned_values.root_module.resources[_]
	acl.type == "aws_s3_bucket_acl"
	#acl.values.bucket == input.planned_values.root_module.resources[_].values.id # Correct bucket ID reference
	acl.values.acl == "private"
}

has_aws_s3_bucket_log if {
	bucket := input.planned_values.root_module.resources[_]
	bucket.type == "aws_s3_bucket"
	bucket.values.bucket
}

has_aws_s3_bucket_acl_log if {
	acl := input.planned_values.root_module.resources[_]
	acl.type == "aws_s3_bucket_acl"
	#acl.values.bucket == input.planned_values.root_module.resources[_].values.id # Correct bucket ID reference
	acl.values.acl == "log-delivery-write"
}

has_aws_s3_bucket_logging_example if {
	logging := input.planned_values.root_module.resources[_]
	logging.type == "aws_s3_bucket_logging"
	##logging.values.bucket == input.planned_values.root_module.resources[_].values.id # Correct bucket ID reference for example bucket
	##logging.values.target_bucket == input.planned_values.root_module.resources[_].values.id # Correct bucket ID reference for log bucket
	logging.values.target_prefix == "log/"
}

valid_configuration if {
	has_aws_s3_bucket_example
	has_aws_s3_bucket_acl_example
	has_aws_s3_bucket_log
	has_aws_s3_bucket_acl_log
	has_aws_s3_bucket_logging_example
}
