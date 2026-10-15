# Prompt 438

## Resources

aws_db_subnet_group, aws_internet_gateway, aws_route_table, aws_route_table_association, aws_route_table_association, aws_security_group, aws_subnet, aws_subnet, aws_vpc

## Prompt

Set up a VPC in the AWS region with two subnets in different availability zones, an internet gateway, and a route table for internet access. It also defines a security group to allow access to MySQL and PostgreSQL databases on their default ports from any IP address and creates a database subnet group including both subnets.

## Difficulty

6

## Intent

Has one "aws_vpc" resource:
Includes a "cidr_block" for network configuration

Has two "aws_subnet" resources:
Both subnets are part of the "aws_vpc" resource
Each subnet is located in a different availability zone: "us-west-1a" and "us-west-1b"

Has one "aws_internet_gateway" resource:
Attached to the "aws_vpc" resource

Has one "aws_route_table" resource:
Associated with the "aws_vpc"
Contains a default route that directs traffic to the "aws_internet_gateway"
Applied to both subnets to enable internet access

Has one "aws_security_group" resource:
Associated with the "aws_vpc"
Configured to allow inbound traffic on the default ports for MySQL and PostgreSQL from any IP address

Has one "aws_db_subnet_group" resource:
Includes both "aws_subnet" resources
Facilitates the placement of databases in the specified subnets

