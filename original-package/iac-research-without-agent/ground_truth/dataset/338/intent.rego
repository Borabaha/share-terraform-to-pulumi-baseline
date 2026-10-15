package terraform.validation

import rego.v1

default is_valid_db_instance := false





# Validate aws_db_instance resource
is_valid_db_instance if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_db_instance"
	resource.expressions.allocated_storage.constant_value != null
	resource.expressions.engine.constant_value == "mysql"
	resource.expressions.instance_class.constant_value != null
	resource.expressions.password.constant_value != null
	resource.expressions.username.constant_value != null
	resource.expressions.publicly_accessible.constant_value == true
	resource.expressions.db_subnet_group_name.references != null
	resource.expressions.vpc_security_group_ids.references != null
}



subnets contains resource if {
	resource := input.configuration.root_module.resources[_]
	resource.type == "aws_subnet"
}

# Validate aws_security_group resource
is_valid_security_group if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_security_group"
	# Additional checks for specific ingress/egress rules can be added here
}

# Validate aws_db_subnet_group resource
is_valid_db_subnet_group if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_db_subnet_group"
	count(resource.expressions.subnet_ids) > 0
}
