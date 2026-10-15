package terraform.validation

import rego.v1

default is_valid_terraform_plan := false

# Rule to check for an AWS Glacier Vault resource with 'name' and 'access_policy' attributes
is_valid_glacier_vault if {
	resource := input.planned_values.root_module.resources[_]
	resource.type == "aws_glacier_vault"
	not is_null(resource.values.name)
	not is_null(resource.values.access_policy)
}

# Combined rule to validate the entire Terraform plan
is_valid_terraform_plan if {
	is_valid_glacier_vault
}
