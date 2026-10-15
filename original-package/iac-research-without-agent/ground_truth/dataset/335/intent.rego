package terraform.validation

import rego.v1

default is_valid_db_instance := false

default is_valid_db_subnet_group := false


# Validate aws_db_instance resource
is_valid_db_instance if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_db_instance"
	resource.expressions.allocated_storage.constant_value == 5
	resource.expressions.instance_class.constant_value == "db.t3.micro"
	resource.expressions.engine.constant_value == "postgres"
	resource.expressions.engine_version.constant_value
	resource.expressions.instance_class.constant_value != null
	resource.expressions.password.constant_value != null
	resource.expressions.username.constant_value != null
	#resource.expressions.publicly_accessible.constant_value == false
	resource.expressions.db_subnet_group_name.references != null
	#resource.expressions.vpc_security_group_ids.references != null
}

# Validate aws_db_subnet_group resource
is_valid_db_subnet_group if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_db_subnet_group"
	count(resource.expressions.subnet_ids) > 0
}


