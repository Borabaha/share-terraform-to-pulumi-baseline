package terraform.validation

import rego.v1

default is_configuration_valid := false

default is_valid_iam_instance_profile := false

default is_valid_iam_role := false

default is_valid_iam_role_policy_attachment := false

default is_valid_s3_bucket := false

default is_valid_s3_object := false

default is_valid_eb_app := false

default is_valid_eb_env := false

is_valid_iam_role if {
	some i
	resource := input.resource_changes[i]
	resource.type == "aws_iam_role"
	contains(resource.change.after.assume_role_policy, "ec2.amazonaws.com")
}

is_valid_iam_role_policy_attachment if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_iam_role_policy_attachment"
	resource.expressions.role.references[0]
	resource.expressions.policy_arn.constant_value
}

# Validate aws_iam_instance_profile resource
is_valid_iam_instance_profile if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_iam_instance_profile"
	resource.expressions.role.references[0] #== "aws_iam_role.eb_ec2_role.name"
}

is_valid_s3_bucket if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_s3_bucket"
	resource.name
	resource.expressions.bucket.constant_value == "sampleapril26426"
}

is_valid_s3_object if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_s3_object"
	resource.expressions.bucket.references[0] #== "aws_s3_bucket.sampleapril26426.id"
	resource.expressions.key
	resource.expressions.source
}

# Validate aws_eb_app
is_valid_eb_app if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_elastic_beanstalk_application"
	resource.expressions.name
}

is_valid_eb_app_version if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_elastic_beanstalk_application_version"
	resource.expressions.name
	resource.expressions.application.references[0] #== "aws_elastic_beanstalk_application.myapp.name"
	resource.expressions.bucket.references[0] #== "aws_s3_object.examplebucket_object.bucket"
	resource.expressions.key.references[0] #== "aws_s3_object.examplebucket_object.key"
}

# Validate aws_eb_env
is_valid_eb_env if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_elastic_beanstalk_environment"
	resource.expressions.name
	resource.expressions.application.references[0] #== "aws_elastic_beanstalk_application.myapp.name"
	resource.expressions.solution_stack_name
	#resource.expressions.version_label.references[0] #== "aws_elastic_beanstalk_application_version.version.name"
	some a
	resource.expressions.setting[a].value.references[0] #== "aws_iam_instance_profile.eb_ec2_profile.name"
}

# Combine all checks into a final rule
is_configuration_valid if {
	is_valid_iam_role
	is_valid_iam_role_policy_attachment
	is_valid_iam_instance_profile
	is_valid_s3_bucket
	is_valid_s3_object
	is_valid_eb_app_version
	is_valid_eb_app
	is_valid_eb_env
}
