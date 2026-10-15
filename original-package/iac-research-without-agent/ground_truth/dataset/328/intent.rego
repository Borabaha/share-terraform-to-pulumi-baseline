package terraform.validation

import rego.v1




default is_valid_security_group := false

default is_valid_db_instance := false

default is_valid_db_subnet_group := false





# Validate aws_security_group resource
is_valid_security_group if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_security_group"
	resource.expressions.vpc_id != null
	#resource.expressions.ingress != null
	#resource.expressions.egress != null
	#resource.expressions.tags != null
}

# Validate aws_db_instance resource
is_valid_db_instance if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_db_instance"
	resource.expressions.allocated_storage.constant_value == 5
	resource.expressions.engine.constant_value == "postgres"
	resource.expressions.engine_version.constant_value == "17.1"
	resource.expressions.instance_class != null
	resource.expressions.username != null
	resource.expressions.password != null
	resource.expressions.skip_final_snapshot.constant_value == true
	resource.expressions.identifier.constant_value == "dolphinscheduler"
}

# Validate aws_db_subnet_group resource
is_valid_db_subnet_group if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_db_subnet_group"
	resource.expressions.subnet_ids != null
	count(resource.expressions.subnet_ids) > 0
}

# Helper function to ensure subnet_ids reference private subnets
private_subnet_ids(subnet_ids) if {
	some i
	subnet := input.configuration.root_module.resources[i]
	subnet.type == "aws_subnet"
	subnet.expressions.tags.Type == "private"
	subnet.expressions.id == subnet_ids[_]
}
