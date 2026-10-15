# Prompt 255

## Resources

aws_redshift_cluster, aws_redshift_endpoint_access, aws_redshift_subnet_group, aws_subnet, aws_subnet, aws_vpc

## Prompt

Create an AWS VPC resource with two AWS subnets. Group these subnets in an AWS Redshift subnet group. Create an example basic AWS Redshift cluster and an AWS Redshift endpoint access with this subnet group attached to the cluster.

## Difficulty

4

## Intent

Has one resource "aws_vpc"

Has one resource "aws_subnet"
with one "vpc_id" with value "aws_vpc.{VPC NAME}.id"

Has another resource "aws_subnet"
with one "vpc_id" with value "aws_vpc.{VPC NAME}.id"

Has one resource "aws_redshift_subnet_group"
with both subnet ids in subnet_ids

Has one resource "aws_redshift_cluster"

Has one resource "aws_redshift_endpoint_access"
with the subnet group referenced in subnet_group_name
and the cluster referenced in cluster_identifier

