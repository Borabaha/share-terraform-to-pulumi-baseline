# Prompt 90

## Resources

aws_eks_cluster, aws_eks_fargate_profile, aws_iam_role, aws_iam_role, aws_iam_role_policy_attachment, aws_subnet, aws_subnet, aws_vpc, null_resource, aws_eks_cluster_auth

## Prompt

Create an IAM role for EKS Fargate profiles with the necessary policies for pod execution. Attach the AmazonEKSFargatePodExecutionRolePolicy to the IAM role. Define an AWS EKS Fargate profile for the 'kube-system' namespace, associating it with the EKS cluster and specifying the pod execution role ARN. Ensure that the specified subnets have the required resource tag for cluster association. Use a null_resource to patch the Kubernetes deployment 'coredns' in the 'kube-system' namespace, using the EKS cluster's endpoint, certificate authority, and authentication token for communication.

## Difficulty

6

## Intent

Resource "aws_iam_role" "eks-fargate-profile"
has one "name"
has one "assume_role_policy"
Resource "aws_iam_role_policy_attachment" "eks-fargate-profile"
has one "policy_arn"
has one "role"
Resource "aws_eks_fargate_profile" "kube-system"
has one "cluster_name"
has one "fargate_profile_name"
has one "pod_execution_role_arn"
has one "subnet_ids"
has one "namespace" in "selector"
Data "aws_eks_cluster_auth" "eks"
has one "name"
Resource "null_resource" "k8s_patcher"
has multiple "triggers" (endpoint, ca_crt, token)
uses a "local-exec" provisioner to execute a command that patches the Kubernetes deployment
has a "lifecycle" policy to ignore changes in "triggers"

