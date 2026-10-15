# Prompt 92

## Resources

aws_eks_access_policy_association, aws_eks_cluster, aws_iam_role, aws_iam_user, aws_subnet, aws_vpc

## Prompt

Create a Terraform script to associate an access policy with name "example", with an AWS EKS cluster. Define a resource linking the cluster's name to a specific policy ARN and a principal's ARN. Include settings for an access scope limited to a specific namespace.

## Difficulty

4

## Intent

has one "aws_eks_access_policy_association" resource
with one "cluster_name"
with one "policy_arn"
with one "principal_arn"
with one "access_scope"

