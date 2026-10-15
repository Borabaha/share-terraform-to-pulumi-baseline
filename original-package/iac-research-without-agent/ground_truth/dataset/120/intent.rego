package terraform.validation

import rego.v1

default has_aws_s3_bucket := false

default has_aws_s3_bucket_ownership_controls := false

#default has_aws_s3_bucket_acl := false

has_aws_s3_bucket if {
	bucket := input.planned_values.root_module.resources[_]
	bucket.type == "aws_s3_bucket"
	bucket.name
	bucket.values.bucket
}

has_aws_s3_bucket_ownership_controls if {
	ownership_controls := input.planned_values.root_module.resources[_]
	ownership_controls.type == "aws_s3_bucket_ownership_controls"
	ownership_controls.name == "example"
	#ownership_controls.values.bucket == input.planned_values.root_module.resources[_].values.id # Correct bucket ID reference
	ownership_controls.values.rule[0].object_ownership == "BucketOwnerPreferred"
}

#has_aws_s3_bucket_acl if {
#	acl := input.planned_values.root_module.resources[_]
#	acl.type == "aws_s3_bucket_acl"
#	acl.name == "example"
#	acl.values.bucket == input.planned_values.root_module.resources[_].values.id # Correct bucket ID reference
#	acl.values.acl == "private"
#	dependency := acl.depends_on[_]
#	dependency == "aws_s3_bucket_ownership_controls.example"
#}

valid_configuration if {
	has_aws_s3_bucket
	has_aws_s3_bucket_ownership_controls
#	has_aws_s3_bucket_acl
}
