package s3_bucket_ownership_controls

import rego.v1

default valid := false


valid if {
	some bucket in input.configuration.root_module.resources
	bucket.type == "aws_s3_bucket"
	bucket.expressions.bucket.constant_value == "mybucket"

	some ownership_controls in input.configuration.root_module.resources
	ownership_controls.type == "aws_s3_bucket_ownership_controls"
	#ownership_controls.expressions.bucket.constant_value == bucket.expressions.bucket.constant_value
	#some rule in ownership_controls.expressions.rule
	#rule.object_ownership.constant_value == "BucketOwnerPreferred"
}
