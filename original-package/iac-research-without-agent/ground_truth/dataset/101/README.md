# Prompt 101

## Resources

aws_eks_cluster, aws_iam_role, aws_iam_role_policy_attachment, aws_subnet, aws_subnet, aws_vpc

## Prompt

Generate a Terraform configuration to create an AWS IAM role called "demo" with attribute name set to "eks-cluster-demo", for an Amazon EKS cluster. The role should allow assuming roles for EKS services and have the AmazonEKSClusterPolicy attached. Additionally, create an AWS EKS cluster with the name "demo" and configure its VPC with specified subnet IDs from in the us-east-1 region. Ensure dependency handling for the IAM role's policy attachment during EKS cluster management.

## Difficulty

4

## Intent

has one "aws_iam_role"
with one "name"
with one "assume_role_policy" 

has one "aws_iam_role_policy_attachment" 
with one "policy_arn"
with one "role" referencing the "aws_iam_role.demo.name"

has one "variable" block for "cluster_name"
with one "default"
with one "type"
with one "description"
with one "nullable"

has one "aws_eks_cluster" 
with one "name"
with one "role_arn" referencing the "aws_iam_role.demo.arn"
with one "vpc_config" containing "subnet_ids"
with dependencies on one IAM role policy attachment

