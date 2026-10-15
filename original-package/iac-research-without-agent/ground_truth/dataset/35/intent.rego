package terraform.validation

import rego.v1

default has_valid_resources := false

# Rule for aws_iam_role resource
has_valid_iam_role(resources) if {
	some resource in resources
	resource.type == "aws_iam_role"
	contains(resource.change.after.assume_role_policy, "codebuild.amazonaws.com")
}

has_valid_codebuild if {
	some i
	resource := input.planned_values.root_module.resources[i]
	resource.type == "aws_codebuild_project"
	resource.values.artifacts
	resource.values.environment[_].environment_variable
	resource.values.name
	resource.values.source[_].type == "NO_SOURCE"
	role := input.configuration.root_module.resources[i]
	role.expressions.service_role
}

has_valid_resources if {
	has_valid_iam_role(input.resource_changes)
	has_valid_codebuild
}
