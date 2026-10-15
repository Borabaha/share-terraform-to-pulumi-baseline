# Prompt 100

## Resources

aws_eks_cluster, aws_iam_role, aws_iam_role_policy_attachment, aws_iam_role_policy_attachment, aws_subnet, aws_subnet, aws_vpc, aws_iam_policy_document

## Prompt

Create a Terraform configuration to set up an AWS IAM role (demo_eks) for an Amazon EKS cluster. The role should allow assuming roles for EKS services and have policies attached for AmazonEKSClusterPolicy and AmazonEKSVPCResourceController. Also, create an AWS EKS cluster (demo_eks) with specified VPC configurations. Ensure proper dependency handling for IAM role permissions during cluster management.

## Difficulty

4

## Intent

has one "data" block for "aws_iam_policy_document" containing:
one "effect"
one "principals" block with "type" and "identifiers"
one "actions" list

has one "aws_iam_role" 
with one "name"
with one "assume_role_policy" referencing the data block

has two "aws_iam_role_policy_attachment"
"demo_eks_AmazonEKSClusterPolicy"
with one "policy_arn"
with one "role" referencing the "aws_iam_role.demo_eks.name"
"demo_eks_AmazonEKSVPCResourceController"
with one "policy_arn"
with one "role" referencing the "aws_iam_role.demo_eks.name"

has one "aws_eks_cluster"
with one "name"
with one "role_arn" referencing the "aws_iam_role.demo_eks.arn"
with one "vpc_config" containing "subnet_ids"
with dependencies on two IAM role policy attachments

has one "data" block for "aws_eks_cluster" 
with one "name" referencing the "aws_eks_cluster.demo_eks.name"


