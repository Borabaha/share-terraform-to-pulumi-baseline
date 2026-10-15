# Prompt 98

## Resources

aws_eks_cluster, aws_eks_node_group, aws_iam_role, aws_iam_role_policy_attachment, aws_iam_role_policy_attachment, aws_iam_role_policy_attachment, aws_subnet, aws_subnet, aws_vpc

## Prompt

Create a Terraform script for an AWS EKS node group (with name attribute set to "example") linked to a specific EKS cluster (with name attribute set to "example"). Define a resource with details including the node group name, node role ARN, and subnet IDs. Configure scaling parameters (desired size is 1, max size is 2, and min size is 1, with max unavailable set to 1) and update settings for node management. Include dependencies on IAM role policy attachments to ensure proper permissions management during lifecycle events of EC2 instances and network interfaces (in particular, make sure the EKS worker node policy, the EKS CNI policy, and the EC2 container registry read only policy are attached).

## Difficulty

6

## Intent

has one "aws_eks_node_group" resource
with one "cluster_name"
with one "node_group_name"
with one "node_role_arn"
with one "subnet_ids"
with one "scaling_config" containing:
one "desired_size"
one "max_size"
one "min_size"
with one "update_config" containing:
one "max_unavailable"
with dependencies on three IAM role policy attachments

