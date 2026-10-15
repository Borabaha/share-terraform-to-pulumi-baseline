# Prompt 91

## Resources

aws_eks_access_entry, aws_eks_cluster, aws_iam_role, aws_subnet, aws_vpc

## Prompt

Create a Terraform script for an AWS EKS access entry with name "example". Define a resource to grant access to an EKS cluster using the cluster's name and a principal's ARN. Include assigning specific Kubernetes groups and set the access type to 'STANDARD'.

## Difficulty

4

## Intent

has one "aws_eks_access_entry" resource
with one "cluster_name"
with one "principal_arn"
with one "kubernetes_groups"
with one "type"

