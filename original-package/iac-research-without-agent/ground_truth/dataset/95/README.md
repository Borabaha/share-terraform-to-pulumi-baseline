# Prompt 95

## Resources

aws_eks_cluster, aws_eks_fargate_profile, aws_iam_role, aws_subnet, aws_subnet, aws_vpc

## Prompt

Generate a Terraform script to create an AWS EKS Fargate profile. Define a resource that links to an EKS cluster (with name set to "example") by name, sets a Fargate profile name, and assigns a pod execution role ARN (tied to an IAM role with name "example"). Specify subnet IDs and include a selector for the namespace 'example'.

## Difficulty

4

## Intent

has one "aws_eks_fargate_profile" resource
with one "cluster_name"
with one "fargate_profile_name"
with one "pod_execution_role_arn"
with one "subnet_ids"
with one "selector" containing "namespace"

