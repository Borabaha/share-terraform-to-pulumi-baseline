package terraform.validation

import rego.v1

default has_aws_eks_cluster_example := false

default has_output_endpoint := false

default has_output_kubeconfig_certificate_authority_data := false

has_aws_eks_cluster_example if {
	cluster := input.configuration.root_module.resources[_]
	cluster.type == "aws_eks_cluster"
	cluster.name == "example"
	cluster.expressions.role_arn != null
	#count(cluster.expressions.vpc_config[_].subnet_ids.references) == 4 # Ensure there are exactly two subnet IDs
	#count(cluster.depends_on) == 2 # Checks for two dependencies
}

has_output_endpoint if {
	endpoint := input.configuration.root_module.outputs[_]
	contains(endpoint.expression.references[_], "aws_eks_cluster.example.endpoint")
}

has_output_kubeconfig_certificate_authority_data if {
	ca_data := input.configuration.root_module.outputs[_]
	contains(ca_data.expression.references[_], "aws_eks_cluster.example.certificate_authority") # Ensures it references aws_eks_cluster.example.certificate_authority[0].data correctly
}

valid_configuration if {
	has_aws_eks_cluster_example
	has_output_endpoint
	has_output_kubeconfig_certificate_authority_data
}
