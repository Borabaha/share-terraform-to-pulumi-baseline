package terraform.analysis

import rego.v1

default has_aws_iam_role := false

default has_aws_iam_role_policy_attachment := false

default has_aws_eks_cluster := false

find_resource(rtype) := resource if {
	resource = input.configuration.root_module.resources[_]
	resource.type == rtype
}

has_aws_iam_role if {
	r := find_resource("aws_iam_role")
	r.expressions.name.constant_value == "eks-cluster-demo"
	r.expressions.assume_role_policy
}

has_aws_iam_role_policy_attachment if {
	r := input.configuration.root_module.resources[_]
	r.type == "aws_iam_role_policy_attachment"
	r.expressions.policy_arn.constant_value == "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
	r.expressions.role.references[_]
}

has_aws_eks_cluster if {
	r := find_resource("aws_eks_cluster")
	r.expressions.role_arn.references[_] != 0
	#count(r.depends_on) == 1
}

valid_config if {
	has_aws_iam_role
	has_aws_iam_role_policy_attachment
	has_aws_eks_cluster
}
