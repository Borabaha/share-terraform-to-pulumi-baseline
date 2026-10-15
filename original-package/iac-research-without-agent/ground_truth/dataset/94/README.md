# Prompt 94

## Resources

aws_eks_cluster, aws_iam_role, aws_iam_role_policy_attachment, aws_iam_role_policy_attachment, aws_subnet, aws_subnet, aws_vpc

## Prompt

Create a Terraform script for provisioning an AWS EKS cluster with name "example". Define a resource with the cluster's name and associated IAM role ARN. Configure the VPC settings with specific subnet IDs. Include dependencies on IAM role policy attachments for proper resource management during creation and deletion. Finally, add outputs for the cluster's endpoint and the kubeconfig certificate authority data.

## Difficulty

5

## Intent

has one "aws_eks_cluster" resource
with one "name"
with one "role_arn"
with one "vpc_config" containing "subnet_ids"
with dependencies on two IAM role policy attachments

has one "output" for "endpoint"
with one "value"

has one "output" for "kubeconfig-certificate-authority-data"
with one "value"

