package terraform.validation

import rego.v1

default has_valid_resources := false
default has_valid_bucket := false
default has_valid_cloudwatch_log_group := false
default has_valid_cloudwatch_log_stream := false
default has_valid_kinesis_analytics_application := false


has_valid_iam_role(resources) if {
	some resource in resources
	resource.type == "aws_iam_role"
	contains(resource.change.after.assume_role_policy, "kinesisanalytics.amazonaws.com")
}

has_valid_bucket if {
	some i
	resource := input.planned_values.root_module.resources[i]
	resource.type == "aws_s3_bucket"
}

has_valid_cloudwatch_log_group if {
	some i
	resource := input.planned_values.root_module.resources[i]
	resource.type == "aws_cloudwatch_log_group"
	resource.values.name
}

has_valid_cloudwatch_log_stream if {
	some i
	resource := input.planned_values.root_module.resources[i]
	resource.type == "aws_cloudwatch_log_stream"
	resource.values.name
	role := input.configuration.root_module.resources[i]
	role.expressions.log_group_name
}

has_valid_kinesis_analytics_application if {
	some i
	resource := input.planned_values.root_module.resources[i]
	resource.type == "aws_kinesis_analytics_application"
	resource.values.name
	resource.values.cloudwatch_logging_options
}

has_valid_resources if {
	has_valid_bucket
	has_valid_iam_role(input.resource_changes)
	has_valid_cloudwatch_log_group
	has_valid_cloudwatch_log_stream
	has_valid_kinesis_analytics_application
}
