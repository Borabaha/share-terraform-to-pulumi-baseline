package terraform.validation

import rego.v1

default is_configuration_valid := false

default is_valid_iam_role := false

default is_valid_eb_app := false

default is_valid_eb_env := false

default is_valid_db_instance := false

default is_valid_vpc := false

default is_valid_internet_gateway := false

default is_valid_subnet := false

default is_valid_subnet_group := false

default is_valid_security_group := false

default is_valid_route_table := false

default is_valid_route_table_association := false

is_valid_vpc if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_vpc"
	resource.expressions.cidr_block
}

is_valid_internet_gateway if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_internet_gateway"
	resource.expressions.vpc_id.references[0]
}

is_valid_subnet if {
	some i, j
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_subnet"
	resource.expressions.cidr_block

	resource2 := input.configuration.root_module.resources[j]
	resource2.type == "aws_subnet"
	resource2.expressions.cidr_block
	resource2.expressions.vpc_id.references[0] == resource.expressions.vpc_id.references[0]
}

is_valid_subnet_group if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_db_subnet_group"
	resource.expressions.subnet_ids.references[0]
}

is_valid_security_group if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_security_group"
	resource.expressions.vpc_id.references[0]
	#resource.expressions.egress
	#resource.expressions.ingress
}

is_valid_route_table if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_route_table"
	#resource.expressions.route.references[0]
	resource.expressions.vpc_id.references
}

is_valid_route_table_association if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_route_table_association"
	resource.expressions.subnet_id.references[0]
	resource.expressions.route_table_id.references[0]
}

is_valid_iam_role if {
	some i
	resource := input.resource_changes[i]
	resource.type == "aws_iam_role"
	contains(resource.change.after.assume_role_policy, "elasticbeanstalk.amazonaws.com")
}


# Validate aws_eb_app
is_valid_eb_app if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_elastic_beanstalk_application"
	resource.expressions.name
}

# Validate aws_eb_env
is_valid_eb_env if {
	some a
	resource := input.configuration.root_module.resources[a]
	resource.type == "aws_elastic_beanstalk_environment"
	resource.expressions.name
	resource.expressions.application.references[0]
	#resource.expressions.solution_stack_name
}

is_valid_db_instance if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_db_instance"
	has_required_main_db_arguments
}

# Helper rule to check if all required arguments are present and valid
has_required_main_db_arguments if {
	resource := input.configuration.root_module.resources[_]
	resource.type == "aws_db_instance"
	resource.expressions.db_subnet_group_name.references[0]
	resource.expressions.vpc_security_group_ids.references[0]

	# Check for allocated_storage, engine, instance_class, username, password, and skip_final_snapshot
	requirement1(resource.expressions)

	# Check for instance_class validity
	requirement2(resource.expressions)
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
	is_valid_eb_app
	is_valid_eb_env
	is_valid_db_instance
	is_valid_vpc
	is_valid_internet_gateway
	is_valid_subnet
	is_valid_subnet_group
	is_valid_security_group
	is_valid_route_table
	is_valid_route_table_association
}
