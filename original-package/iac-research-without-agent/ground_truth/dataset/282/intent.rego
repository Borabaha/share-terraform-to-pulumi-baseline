package aws_s3_bucket_cors

import rego.v1

default valid := false

valid if { # IF THE BUCKET IS REFERRED TO BY ID
	some bucket in input.configuration.root_module.resources
	bucket.type == "aws_s3_bucket"

	some cors_config in input.configuration.root_module.resources
	cors_config.type == "aws_s3_bucket_cors_configuration"

	bucket.address in cors_config.expressions.bucket.references
}

valid if { # IF THE BUCKET IS REFFERED TO BY NAME
	some bucket in input.configuration.root_module.resources
	bucket.type == "aws_s3_bucket"

	some cors_config in input.configuration.root_module.resources
	cors_config.type == "aws_s3_bucket_cors_configuration"

	cors_config.expressions.bucket.constant_value == bucket.expressions.bucket.constant_value
}
