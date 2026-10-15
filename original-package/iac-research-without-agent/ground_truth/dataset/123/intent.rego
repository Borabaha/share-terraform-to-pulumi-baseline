package terraform.validation

import rego.v1

default has_aws_s3_bucket_example := false

default has_aws_s3_bucket_ownership_controls_example := false

has_aws_s3_bucket_example if {
	bucket := input.planned_values.root_module.resources[_]
	bucket.type == "aws_s3_bucket"
	bucket.values.bucket
}

has_aws_s3_bucket_ownership_controls_example if {
	controls := input.planned_values.root_module.resources[_]
	controls.type == "aws_s3_bucket_ownership_controls"
	#controls.values.bucket == input.planned_values.root_module.resources[_].values.bucket.id # Ensures it's the correct reference to "example" bucket
	controls.values.rule[0].object_ownership == "BucketOwnerPreferred"
}

valid_configuration if {
	has_aws_s3_bucket_example
	has_aws_s3_bucket_ownership_controls_example
}
