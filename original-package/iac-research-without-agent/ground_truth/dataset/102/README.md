# Prompt 102

## Resources

aws_eks_cluster, aws_iam_role, aws_iam_role_policy_attachment, aws_subnet, aws_subnet, aws_vpc

## Prompt

Create a Terraform configuration to provision an AWS IAM role with attribute name set to "example" for an Amazon EKS cluster. The role's assume role policy should allow access for EKS services. Attach the AmazonEKSClusterPolicy to this role. Additionally, define an AWS EKS cluster with a name set to "example", with a subnet and attached VPC. Ensure proper dependency handling for the IAM role's policy attachment during the EKS cluster creation process. The EKS cluster's endpoint private access should be set to false, and endpoint public access set to true

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


