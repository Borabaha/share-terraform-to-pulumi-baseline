# Prompt 99

## Resources

aws_eks_cluster, aws_eks_pod_identity_association, aws_iam_role, aws_iam_role, aws_iam_role_policy_attachment, aws_subnet, aws_subnet, aws_vpc, aws_iam_policy_document

## Prompt

Create a Terraform script for an AWS EKS setup with pod identity management. Start by defining an IAM policy document (called "example") for assuming a role by EKS pods. Then, create an IAM role (called "example") using this policy. Attach a policy for S3 read-only access to this role. Finally, define an EKS pod identity association linking the role to a specific EKS cluster (called "example"), namespace, and service account.

## Difficulty

5

## Intent

has one "data" block for "aws_iam_policy_document" named "assume_role"
with one "statement" block containing:
one "effect"
one "principals" block with "type" and "identifiers"
one "actions" list

has one "aws_iam_role" resource named "example"
with one "name"
with one "assume_role_policy" referencing the data block

has one "aws_iam_role_policy_attachment" resource named "example_s3"
with one "policy_arn"
with one "role" referencing the "aws_iam_role.example.name"

has one "aws_eks_pod_identity_association" resource named "example"
with one "cluster_name"
with one "namespace"
with one "service_account"
with one "role_arn" referencing the "aws_iam_role.example.arn"

