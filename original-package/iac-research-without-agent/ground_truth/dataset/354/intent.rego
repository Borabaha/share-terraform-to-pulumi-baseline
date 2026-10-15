package terraform.validation

import rego.v1

default is_valid_aws_db_proxy := false

default is_valid_aws_rds_cluster := false

default is_valid_aws_security_group := false

default is_valid_aws_db_subnet_group := false

default is_valid_aws_secretsmanager_secret := false

default is_valid_aws_iam_role := false

# Validate aws_db_proxy resource
is_valid_aws_db_proxy if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_db_proxy"
	resource.expressions.engine_family.constant_value == "MYSQL"
	resource.expressions.require_tls.constant_value == true
	resource.expressions.idle_client_timeout.constant_value == 1800
	resource.expressions.debug_logging.constant_value == false
	auth := resource.expressions.auth[_]
	auth.auth_scheme.constant_value == "SECRETS"
}

# Validate aws_rds_cluster resource
is_valid_aws_rds_cluster if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_rds_cluster"
	resource.expressions.engine.constant_value == "aurora-mysql"
	resource.expressions.master_username != null
	resource.expressions.master_password != null
}


# Validate aws_security_group resource
is_valid_aws_security_group if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_security_group"

	# Checks for at least one ingress and one egress rule, more specific validation can be added
	#count(resource.expressions.ingress) > 0
	#count(resource.expressions.egress) > 0
}

# Validate aws_db_subnet_group resource
is_valid_aws_db_subnet_group if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_db_subnet_group"
	count(resource.expressions.subnet_ids) > 0
}

# Validate aws_secretsmanager_secret resource
is_valid_aws_secretsmanager_secret if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_secretsmanager_secret"
	resource.expressions.name_prefix != null
}

# Validate aws_iam_role resource
is_valid_aws_iam_role if {
	some i
	resource := input.configuration.root_module.resources[i]
	resource.type == "aws_iam_role"
	resource.expressions.assume_role_policy != null
}
