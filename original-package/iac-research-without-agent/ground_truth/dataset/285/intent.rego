package aws_s3_bucket_website

import rego.v1

default valid := false

valid if { # IF THE BUCKET IS REFERRED TO BY ID
	some bucket in input.configuration.root_module.resources
	bucket.type == "aws_s3_bucket"

	some website in input.configuration.root_module.resources
	website.type == "aws_s3_bucket_website_configuration"
	some index in website.expressions.index_document
	index.suffix.constant_value == "index.html"

	bucket.address in website.expressions.bucket.references
}

valid if { # IF THE BUCKET IS REFFERED TO BY NAME
	some bucket in input.configuration.root_module.resources
	bucket.type == "aws_s3_bucket"

	some website in input.configuration.root_module.resources
	website.type == "aws_s3_bucket_website_configuration"
	some index in website.expressions.index_document
	index.suffix.constant_value == "index.html"

	website.expressions.bucket.constant_value == bucket.expressions.bucket.constant_value
}
