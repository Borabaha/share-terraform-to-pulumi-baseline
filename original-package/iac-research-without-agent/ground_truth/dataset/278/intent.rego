package aws_s3_object

import rego.v1

default valid := false


valid if {
	some bucket in input.configuration.root_module.resources
	bucket.type == "aws_s3_bucket"

	some object in input.configuration.root_module.resources
	object.type == "aws_s3_object"
	#bucket.address in object.expressions.bucket.references
	object.expressions.source.constant_value == "assets/test.pdf"
}
