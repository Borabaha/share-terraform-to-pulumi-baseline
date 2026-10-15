package terraform.validation

import rego.v1

#default has_aws_iam_policy_document_assume_role_eks := false

default has_aws_iam_role_demo_eks := false

default has_aws_iam_role_policy_attachment_demo_eks_AmazonEKSClusterPolicy := false

default has_aws_iam_role_policy_attachment_demo_eks_AmazonEKSServicePolicy := false

default has_aws_eks_cluster_demo_eks := false

#has_aws_iam_policy_document_assume_role_eks if {   # there are multiple ways to define the assume role policy document
#	assume_role_eks := input.configuration.root_module.resources[_]
#	assume_role_eks.type == "aws_iam_policy_document"
#	assume_role_eks.expressions.statement[_].effect.constant_value == "Allow"
#	assume_role_eks.expressions.statement[_].principals[_].type.constant_value == "Service"
#	assume_role_eks.expressions.statement[_].principals[_].identifiers.constant_value[_] == "eks.amazonaws.com"
#	assume_role_eks.expressions.statement[_].actions.constant_value[_] == "sts:AssumeRole"
#}

has_aws_iam_role_demo_eks if {
	role := input.configuration.root_module.resources[_]
	role.type == "aws_iam_role"
	role.name
	role.expressions.assume_role_policy != null
}

has_aws_iam_role_policy_attachment_demo_eks_AmazonEKSClusterPolicy if {
	policy_attachment := input.planned_values.root_module.resources[_]
	policy_attachment.type == "aws_iam_role_policy_attachment"
	policy_attachment.name
	policy_attachment.values.policy_arn == "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
	policy_attachment.values.role != null
}

has_aws_iam_role_policy_attachment_demo_eks_AmazonEKSServicePolicy if {
	policy_attachment := input.planned_values.root_module.resources[_]
	policy_attachment.type == "aws_iam_role_policy_attachment"
	policy_attachment.name
	policy_attachment.values.policy_arn == "arn:aws:iam::aws:policy/AmazonEKSServicePolicy"
	policy_attachment.values.role != null
}

has_aws_eks_cluster_demo_eks if {
	eks_cluster := input.configuration.root_module.resources[_]
	eks_cluster.type == "aws_eks_cluster"
	eks_cluster.name
	eks_cluster.expressions.role_arn != null
	eks_cluster.expressions.vpc_config[0].subnet_ids != null

	count(eks_cluster.depends_on) == 2


}

valid_configuration if {
	#has_aws_iam_policy_document_assume_role_eks
	has_aws_iam_role_demo_eks
	has_aws_iam_role_policy_attachment_demo_eks_AmazonEKSClusterPolicy
	has_aws_iam_role_policy_attachment_demo_eks_AmazonEKSServicePolicy
	has_aws_eks_cluster_demo_eks
}
