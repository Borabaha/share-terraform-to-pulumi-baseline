# Prompt 87

## Resources

aws_eks_cluster, aws_iam_role, aws_iam_role_policy_attachment, aws_iam_role_policy_attachment, aws_subnet, aws_vpc, aws_region

## Prompt

Define a variable 'cluster_name' of type string. Create an AWS EKS cluster named based on the provided cluster name variable, associating it with an IAM role. Configure the EKS cluster with VPC subnet IDs for networking. Ensure that IAM role permissions are handled before and after EKS cluster management for proper resource handling. Use local-exec provisioners to manage kubectl configuration during cluster creation and destruction. Define an IAM role with a policy attachment for Amazon EKS cluster and service policies.

## Difficulty

6

## Intent

has one "aws_eks_cluster" resource
with one "name"
with one "role_arn"
with one "subnet_ids" in "vpc_config"
with multiple "depends_on" dependencies
with multiple "local-exec" provisioners 
with a "command"
with a "when" 

has one "aws_iam_role" resource
with one "name"
with one "assume_role_policy"

has one "aws_iam_role_policy_attachment" resource for "eks_cluster_policy"
with one "policy_arn"
with one "role"

has one "aws_iam_role_policy_attachment" resource for "eks_service_policy"
with one "policy_arn"
with one "role"

