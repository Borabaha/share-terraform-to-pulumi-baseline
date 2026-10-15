package terraform.validation

import rego.v1

default valid_configuration := false

default has_s3_bucket := false

default has_aws_s3_bucket_acl := false

default has_aws_s3_bucket_public_access_block := false

default has_aws_s3_bucket_server_side_encryption_configuration := false

has_s3_bucket if {
	resource := input.configuration.root_module.resources[_]
	resource.type == "aws_s3_bucket"
	resource.expressions.bucket.constant_value == "test-bucket"
	#some i
	#resource.expressions.bucket.references[i] == "var.bucket_name"
}

has_aws_s3_bucket_acl if {
	resource := input.configuration.root_module.resources[_]
	resource.type == "aws_s3_bucket"
	resource.name != 0
	#resource.expressions.acl.constant_value != null
}

has_aws_s3_bucket_public_access_block if {
	resource := input.configuration.root_module.resources[_]
	resource.type == "aws_s3_bucket_public_access_block"
	resource.expressions.bucket.references != null
}

has_aws_s3_bucket_server_side_encryption_configuration if {
	resource := input.configuration.root_module.resources[_]
	#resource.type == "aws_s3_bucket"
	resource.name != 0
	some i, j, k
	resource.expressions.server_side_encryption_configuration[i].rule[j].apply_server_side_encryption_by_default[k].sse_algorithm.constant_value == "AES256" != null
}

valid_configuration if {
	has_s3_bucket
	has_aws_s3_bucket_acl
	has_aws_s3_bucket_public_access_block
	has_aws_s3_bucket_server_side_encryption_configuration
}
