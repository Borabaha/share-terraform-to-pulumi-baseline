package terraform.validation

import rego.v1

default has_aws_eks_addon_example := false

has_aws_eks_addon_example if {
	addon := input.planned_values.root_module.resources[_]
	addon.type == "aws_eks_addon"
	addon.name
	addon.values.cluster_name == input.planned_values.root_module.resources[_].values.name # Ensures it references aws_eks_cluster.example correctly
	addon.values.addon_name == "vpc-cni"
}
