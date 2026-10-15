package terraform.validation

import rego.v1

default has_s3_bucket := false

default has_s3_bucket_logging := false

default valid_configuration := false

has_s3_bucket if {
	bucket := input.configuration.root_module.resources[_]
	bucket.type == "aws_s3_bucket"
	bucket.expressions.bucket.constant_value == "a"
}

has_s3_bucket_logging if {
    logging := input.planned_values.root_module.resources[_]
    logging.type == "aws_s3_bucket_logging"
    #logging.values.bucket == "testbucketineu-west2"
    #logging.values.target_bucket == "logging-680235478471"
    logging.values.target_prefix == "log/"
}

valid_configuration if {
	has_s3_bucket
	has_s3_bucket_logging
}
