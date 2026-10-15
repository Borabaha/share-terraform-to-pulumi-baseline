package terraform.validation

import rego.v1

default has_aws_s3_bucket := false

#default has_aws_s3_bucket_acl := false

default has_aws_s3_bucket_policy := false

has_aws_s3_bucket if {
	bucket := input.planned_values.root_module.resources[_]
	bucket.type == "aws_s3_bucket"
	bucket.values.bucket == "my-unique-bucket-name"
}

has_aws_s3_bucket_acl if {
	acl := input.planned_values.root_module.resources[_]
	acl.type == "aws_s3_bucket_acl"
	acl.name == "my_bucket_acl"
	acl.values.bucket == input.planned_values.root_module.resources[_].values.id # Ensure correct bucket reference
	acl.values.acl == "private"
}

has_aws_s3_bucket_policy if {
	policy := input.planned_values.root_module.resources[_]
	policy.type == "aws_s3_bucket_policy"
	policy.name == "my_bucket_policy"
	#policy.values.bucket == input.planned_values.root_module.resources[_].values.id # Ensure correct bucket reference
}

valid_configuration if {
	has_aws_s3_bucket
	#has_aws_s3_bucket_acl
	has_aws_s3_bucket_policy
}
