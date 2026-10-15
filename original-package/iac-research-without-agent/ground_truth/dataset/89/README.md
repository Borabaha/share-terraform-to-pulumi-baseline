# Prompt 89

## Resources

aws_eks_cluster, aws_iam_role, aws_iam_role_policy_attachment, aws_iam_role_policy_attachment, aws_subnet, aws_vpc, aws_region

## Prompt

Set up an AWS provider for the specified region. Retrieve the current caller identity using 'aws_caller_identity'. Optionally, fetch the latest stable ECR image tagged as 'stable' from the specified repository. Define local variables including an image tag, AWS tags, and workspace name. Instantiate an EKS module with configurations for cluster setup, IAM policies, instance types, and node count. Retrieve information about the created EKS cluster and its authentication data. Configure Helm and Kubernetes providers using the EKS cluster's details for cluster communication.

## Difficulty

6

## Intent

has one "aws_caller_identity" data source named "current"
has one "aws_ecr_image" 
with one "repository_name"
with one "image_tag"

has multiple local variables defining:
"image_tag" 
"aws_tags"
"workspace_name"

has one module named "eks"

has one "aws_eks_cluster" data source named "aptos"
with one "name"
with a "depends_on" 
has one "aws_eks_cluster_auth"
with one "name"

has one "helm" provider
has one "kubernetes" provider


