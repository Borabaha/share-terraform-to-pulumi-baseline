# Prompt 431

## Resources

aws_internet_gateway, aws_route_table, aws_vpc

## Prompt

sets up a dedicated-tenancy AWS VPC with DNS support and hostnames enabled, an internet gateway, and a route table for outbound internet access, all tagged with a variable name.

## Difficulty

3

## Intent

Has one "aws_vpc" resource
with a specified "cidr_block"
with "enable_dns_support" and "enable_dns_hostnames" set to true

Has one "aws_internet_gateway" resource
with "vpc_id" referencing the "aws_vpc" resource
with a "tags" map including a "Name" key referencing a variable

Has one "aws_route_table" resource
with "vpc_id" referencing the "aws_vpc" resource
containing a default route for internet access through the "aws_internet_gateway"
with a "tags" map including a "Name" key referencing a variable

