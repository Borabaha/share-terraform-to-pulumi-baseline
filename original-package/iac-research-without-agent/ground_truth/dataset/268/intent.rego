package aws_s3

import rego.v1

default valid := false

valid if {
	some bucket in input.configuration.root_module.resources
	bucket.type == "aws_s3_bucket"
}
