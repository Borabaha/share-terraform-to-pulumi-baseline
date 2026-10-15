# Prompt 88

## Resources

aws_eks_cluster, aws_iam_role, aws_iam_role_policy_attachment, aws_subnet, aws_subnet, aws_subnet, aws_subnet, aws_vpc

## Prompt

Create an IAM role named 'eks-cluster-1' with an assume role policy allowing the 'eks.amazonaws.com' service to assume the role. Attach the 'AmazonEKSClusterPolicy' IAM policy to this role. Define an AWS EKS cluster named based on the provided cluster name variable and version, associating it with the IAM role. Configure the cluster's VPC with subnet IDs for networking, including private and public subnets in the specified AWS region.

## Difficulty

5

## Intent

has one "aws_iam_role" resource
with one "name"
with one "assume_role_policy"

has one "aws_iam_role_policy_attachment"
with one "policy_arn"
with one "role"

has one "aws_eks_cluster" resource named "cluster"
with one "name"
with one "version"
with one "role_arn"
with one "subnet_ids" in "vpc_config"
with one "depends_on" dependency

