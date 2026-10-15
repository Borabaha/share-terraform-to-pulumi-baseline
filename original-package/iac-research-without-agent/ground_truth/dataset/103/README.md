# Prompt 103

## Resources

aws_eks_cluster, aws_iam_role, aws_iam_role_policy_attachment, aws_subnet, aws_subnet, aws_vpc

## Prompt

Generate Terraform code to set up an AWS IAM role named 'eks-cluster' for an Amazon EKS cluster. Ensure the role's assume role policy allows access for EKS services and attach the AmazonEKSClusterPolicy to this role. Create an AWS EKS cluster with a name and version, attaching it to a subnet and VPC from us-east-1. Ensure proper dependency handling for the IAM role's policy attachment during EKS cluster creation. The EKS cluster's endpoint private access should be set to false, and endpoint public access set to true

## Difficulty

4

## Intent

has one "aws_iam_role" 
with one "name"
with one "assume_role_policy"

has one "aws_iam_role_policy_attachment"
with one "policy_arn"
with one "role" referencing the "aws_iam_role.eks.name"

has one "aws_eks_cluster"
with one "name"
with one "version"
with one "role_arn"
with one "vpc_config" containing "endpoint_private_access", "endpoint_public_access", and "subnet_ids"

