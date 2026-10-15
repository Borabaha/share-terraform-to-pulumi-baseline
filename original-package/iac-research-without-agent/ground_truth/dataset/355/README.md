# Prompt 355

## Resources

aws_db_proxy, aws_db_subnet_group, aws_iam_role, aws_rds_cluster, aws_secretsmanager_secret, aws_secretsmanager_secret_version, aws_security_group, aws_security_group, aws_subnet, aws_subnet, aws_vpc

## Prompt

Set up an AWS RDS Aurora MySQL cluster with a proxy for enhanced connection management, including VPC, subnets, security groups, IAM roles, and Secrets Manager for secure credential storage. The backup retention period for rds cluster should be 5, and the preffered backup window is 7 am to 9 am.

## Difficulty

6

## Intent

has one "aws_db_proxy" resource
with "engine_family" = "MYSQL"
with "require_tls" = true
with "auth_scheme" = "SECRETS"

has one "aws_rds_cluster" resource
with "engine" = "aurora-mysql"
with "master_username" and "master_password" from variables

has one "aws_vpc" resource
with a "cidr_block"

has one "aws_subnet" resource
with two instances for different availability zones

has one "aws_security_group" resource
with ingress and egress rules for RDS and EC2 instances

has one "aws_db_subnet_group" resource
with subnet IDs

has one "aws_secretsmanager_secret" resource
with DB credentials

has one "aws_iam_role" resource
for the RDS proxy with an assume role policy

