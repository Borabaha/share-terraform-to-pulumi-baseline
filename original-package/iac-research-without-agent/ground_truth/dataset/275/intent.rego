package s3_bucket_metric

import rego.v1

default valid := false
default bucket_exists := false
default metric_exists := false

# Check if an S3 bucket named "mybucket" exists
bucket_exists if {
    some bucket in input.configuration.root_module.resources
    bucket.type == "aws_s3_bucket"
    bucket.expressions.bucket.constant_value == "mybucket"
}

# Check if an S3 bucket metric exists
metric_exists if {
    some metrics in input.configuration.root_module.resources
    metrics.type == "aws_s3_bucket_metric"
}


# The configuration is only valid if all conditions are met
valid if {
    bucket_exists
    metric_exists
}
