package terraform.validation

import rego.v1

default is_configuration_valid := false

default is_valid_iam_instance_profile := false

default is_valid_iam_role := false

default is_valid_iam_role_policy_attachment := false

default is_valid_eb_app := false

default is_valid_eb_env := false

default is_valid_db_instance := false

default is_valid_r53_zone := false

default is_valid_r53_record := false

# Validate aws_route53_zone resource
is_valid_r53_zone if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_route53_zone"
	resource.name
}

# Validate aws_route53_record
is_valid_r53_record if {
	some i, j
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_route53_record"
	resource.provider_config_key == "aws.us_east_1"
	resource.expressions.name
	resource.expressions.type
	resource.expressions.ttl
	resource.expressions.set_identifier
	resource.expressions.latency_routing_policy[0].region.constant_value == "us-east-1"
	resource.expressions.records.references[0] == "aws_elastic_beanstalk_environment.myenv_us_east.cname"
	resource.expressions.zone_id.references[0]

	resource2 := input.configuration.root_module.resources[j]
	resource2.type == "aws_route53_record"
	resource2.provider_config_key == "aws.eu_west_1"
	resource2.expressions.name
	resource2.expressions.type
	resource2.expressions.ttl
	resource2.expressions.set_identifier
	resource2.expressions.latency_routing_policy[0].region.constant_value == "eu-west-1"
	resource2.expressions.records.references[0] == "aws_elastic_beanstalk_environment.myenv_eu_west.cname"
	resource2.expressions.zone_id.references[0]
}

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
	resource.expressions.policy_arn.constant_value == "arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier"
}

# Validate aws_iam_instance_profile resource
is_valid_iam_instance_profile if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_iam_instance_profile"
	resource.expressions.role.references[0]
}

# Validate aws_eb_app
is_valid_eb_app if {
	some i, j
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_elastic_beanstalk_application"
	resource.expressions.name
	resource.provider_config_key == "aws.us_east_1"

	resource2 := input.configuration.root_module.resources[j]
	resource2.type == "aws_elastic_beanstalk_application"
	resource2.expressions.name
	resource2.provider_config_key == "aws.eu_west_1"
}

# Validate aws_eb_env
is_valid_eb_env if {
	some i, j
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_elastic_beanstalk_environment"
	resource.provider_config_key == "aws.us_east_1"
	resource.expressions.name
	resource.expressions.application.references[0] == "aws_elastic_beanstalk_application.myapp_us_east.name"
	resource.expressions.solution_stack_name

	resource2 := input.configuration.root_module.resources[j]
	resource2.type == "aws_elastic_beanstalk_environment"
	resource2.provider_config_key == "aws.eu_west_1"
	resource2.expressions.name
	resource2.expressions.application.references[0] == "aws_elastic_beanstalk_application.myapp_eu_west.name"
	resource2.expressions.solution_stack_name

}

is_valid_db_instance if {
	resource := input.configuration.root_module.resources[_]
	resource.type == "aws_db_instance"
	has_required_main_db_arguments
}

# Helper rule to check if all required arguments are present and valid
has_required_main_db_arguments if {
	some i, j
	resource := input.configuration.root_module.resources[i]
	resource2 := input.configuration.root_module.resources[j]
	resource.type == "aws_db_instance"
	resource.provider_config_key == "aws.us_east_1"
	resource2.type == "aws_db_instance"
	resource2.provider_config_key == "aws.eu_west_1"

	# Check for allocated_storage, engine, instance_class, username, password, and skip_final_snapshot
	requirement1(resource.expressions)
	requirement1(resource2.expressions)

	# Check for instance_class validity
	requirement2(resource.expressions)
	requirement2(resource2.expressions)
}

# 1, allocated_storage and engine or snapshot_identifier or replace_source_db
requirement1(expressions) if {
	expressions.allocated_storage
	expressions.engine
	expressions.username
	expressions.password
	is_valid_engine(expressions.engine.constant_value)
}

requirement1(expressions) if {
	expressions.snapshot_identifier
}

# Check for instance_class validity
requirement2(expressions) if {
	expressions.instance_class
	is_valid_instance_class(expressions.instance_class.constant_value)
}

# Helper rule to validate engine value
is_valid_engine(engine) if {
	engine_set := {
		"mysql",
		"postgres",
		"mariadb",
		"oracle-se",
		"oracle-se1",
		"oracle-se2",
		"oracle-ee",
		"sqlserver-ee",
		"sqlserver-se",
		"sqlserver-ex",
		"sqlserver-web",
	}
	engine_set[engine]
}

# Helper rule to validate instance class type
is_valid_instance_class(instance_class) if {
	instance_class_starts_with(instance_class, "db.")
}

# Helper rule to check prefix of instance class
instance_class_starts_with(instance_class, prefix) if {
	startswith(instance_class, prefix)
}

# Combine all checks into a final rule
is_configuration_valid if {
	is_valid_iam_role
	is_valid_iam_role_policy_attachment
	is_valid_iam_instance_profile
	is_valid_eb_app
	is_valid_eb_env
	is_valid_db_instance
	is_valid_r53_zone
	is_valid_r53_record
}
