# Prompt 97

## Resources

aws_eks_cluster, aws_eks_identity_provider_config, aws_iam_role, aws_subnet, aws_subnet, aws_vpc

## Prompt

Generate a Terraform script to configure an OIDC identity provider for an AWS EKS cluster (where the cluster has it's name attribute set to "example"). Define a resource that links to the cluster by name and sets up OIDC with specific parameters including client ID, identity provider config name, and issuer URL.

## Difficulty

4

## Intent

has one "aws_eks_identity_provider_config" resource
with one "cluster_name"
with one "oidc" block containing:
one "client_id"
one "identity_provider_config_name"
one "issuer_url"

