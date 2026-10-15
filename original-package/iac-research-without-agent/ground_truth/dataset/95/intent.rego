package terraform.validation

import rego.v1

default has_aws_eks_fargate_profile_example := false

has_aws_eks_fargate_profile_example if {
	fargate_profile := input.configuration.root_module.resources[_]
	fargate_profile.type == "aws_eks_fargate_profile"
	fargate_profile.name
	fargate_profile.expressions.cluster_name.references[_] # Ensures it references aws_eks_cluster.example correctly
	fargate_profile.expressions.fargate_profile_name.constant_value
	fargate_profile.expressions.pod_execution_role_arn.references[_] # Ensures it references aws_iam_role.example correctly
	fargate_profile.expressions.selector[_].namespace.constant_value == "example"
}
